require 'json'
require 'ox'

#
# bioproject.xmlをjsonに変換するクラス
#
class BPXml2JsonConverter
    #
    # コンストラクタ
    #
    # @param [String] bp_xml bioproject.xml から切り出したXMLエレメント
    #
    def initialize(bp_xml)
        begin
            xml = Ox.parse(bp_xml)
            project = xml.Project
        rescue
            print bp_xml
            raise
        end

        @hash = {
            'type' => 'bioproject',
            'identifier' => project.locate('Project/ProjectID/ArchiveID/@accession')[0], # "//ProjectID/ArchiveID/@accession"
            'organism' => project.locate('Project/ProjectDescr/Name')[0]&.text, # "//Project/Project/ProjectDescr/Name"
            'title' => project.locate('Project/ProjectDescr/Title')[0]&.text, # "//Project/Project/ProjectDescr/Title"
            'description' => project.locate('Project/ProjectDescr/Description')[0]&.text, # "//Project/ProjectDescr/Description"
            'data type' =>  project.locate('Project/ProjectTypeSubmission/ProjectDataTypeSet/DataType')[0]&.text, # "//ProjectTypeSubmission/ProjectDataTypeSet/DataType"
            'organization' => project.locate('Project/Submission/Description/Organization/Name')[0]&.text, # "//Submission/Description/Organization/Name"
            'publication' => project.locate('Project/ProjectDescr/Publication').map do |elm| # "//Project/ProjectDescr/Publication"
                {'id' => elm.id, 'Title' => elm.locate('Title')[0]&.text}
            end,
            'properties' => nil,
            'dbXrefs' => project.locate('Project/ProjectDescr/LocusTagPrefix').map do |elm| # "//Project/ProjectDescr/LocusTagPrefix/@biosample_id"
                elm.locate('@biosample_id')
            end,
            'distribution' => nil,
            'Download' => nil,
            'status' => project.locate('Project/Submission/Description/Access')[0]&.text,
            'visibility' => nil
        }
        # 以下、Pythonコードからコピー
        # Todo: 以下ElasticSearchの項目がDate型なため空の値を登録できない（レコードのインポートがエラーとなりスキップされる）
        submission = project.locate('Project/Submission')[0]
        if submission
            @hash['dateCreated'] = submission.submitted if submission.submitted
            @hash['dateModified'] = submission.last_update if submission.last_update
        end
        date_published = project.locate('Project/ProjectDescr/ProjectReleaseDate')[0]&.text
        @hash['datePublished'] = date_published if date_published
    end

    #
    # XMLエレメントを所定の形式のjsonに変換します。
    #
    def to_json
        @hash.to_json
    end

    #
    # XMLエレメントから所定のメタ情報のjsonを出力します。
    #
    def meta_json
        {index: {_index: 'bioproject', _type: 'metadata', _id: @hash['identifier']}}.to_json
    end

    #
    # XMLエレメントをメタ情報と所定の形式のjsonのセットで出力します。
    #
    def to_json_with_meta
        "#{meta_json}\n#{to_json}"
    end
end

#
# Python の etree.iterparse と類似の機能を提供するクラス
#
class XmlFileLazyReader
    #
    # コンストラクタ
    #
    # @param [String] file_path XMLファイルのパス
    # @param [String] tag XMLファイルから分割して切り出すタグ
    # @param [Integer] buffer_kbytes XMLファイルを読み込む際のバッファーサイズ(KB)。初期値: 16
    #
    def initialize(file_path, tag, buffer_kbytes = 16)
        raise ArgumentError, 'file_path is not set.' unless file_path.is_a?(String)
        raise ArgumentError, 'tag is not set.' unless tag.is_a?(String)
        raise ArgumentError, 'buffer_kbytes is not Integer.' unless buffer_kbytes.is_a?(Integer)

        @file = File.open(file_path, 'r')
        @buf = ''
        @buffer_size = buffer_kbytes * 1024
        @fiber = Fiber.new do
            @buf = @file.read(@buffer_size)

            loop do
                res = find_tag_index(tag, 0)
                break unless res
                Fiber.yield(@buf.slice!(0..res[:stop_index])[res[:start_index]..-1])
            end
        end
    end

    #
    # XMLを分割したタグごとに取得します。
    #
    def each_element
        loop do
            yield(@fiber.resume)
            unless @fiber.alive?
                return
            end
        end
    end

    private
    def find_tag_index(tag, start_index)
        current_index = start_index
        index1 = 0
        loop do
            index1 = @buf.index("<#{tag}>", current_index)
            while index1 == nil
                return nil unless bufnext
            end
            index2 = @buf.index("<#{tag}>", index1 + tag.length + 1)
            index3 = @buf.index("</#{tag}>", index1 + tag.length + 1)

            # while index3 == nil # 同一タグのネストを考慮 *する* 場合
            while index3 == nil && index2 == nil # 同一タグのネストを考慮 *しない* 場合
                return nil unless buffer_next
                index3 = @buf.index("</#{tag}>", @buffer_size - tag.length - 3)
            end

            # 同一タグのネストを考慮 *する* 場合の実装
            # if index2 && index2 < index3
            #     res = find_tag_index(tag, index2)
            #     current_index = res[:stop_index] + 1
            # else
            #     return {start_index: index1, stop_index: index3 + tag.length + 2}
            # end

            # 同一タグのネストを考慮 *しない* 場合の実装
            if index2 && !index3
                print 'close tag lost '
                index3 = index2 - 1
            end
            return {start_index: index1, stop_index: index3 + tag.length + 2}

        end while(index1)
        return nil
    end

    def buffer_next
        tmp = @file.read(@buffer_size)
        return nil unless tmp
        if @buf.length > 100 * 1024 * 1024
            print "Element size over 100MB [#{@buf.slice(@buf.index('<ArchiveID'), 80)}]"
            @buf = ''
        end
        @buf += tmp
    end
end

#
# bioproject.xml を BPXml2JsonConverter によって jsonl 形式で出力するためのクラス
#
class BPXml2Jsonl
    #
    # コンストラクタ
    #
    # @param [String] out_path jsonファイルの出力先パス
    #
    def initialize(out_path)
        raise ArgumentError, 'out_path is not set.' unless out_path.is_a?(String)

        @to_json_ractor = Ractor.new(out_path) do |out_path|
            File.delete(out_path)
            json = File.open(out_path, 'a')
            loop do
                bp_xml = Ractor.receive
                break unless bp_xml
                json << BPXml2JsonConverter.new(bp_xml).to_json_with_meta + "\n"
            end
        end
    end

    #
    # 渡されたXMLエレメントを変換処理を行うスレッドに渡します。
    #
    # @param [String] xml 変換対象のXMLエレメント
    #
    def send(xml)
        @to_json_ractor.send(xml)
    end
end

print Time.now, " Started\n"
reader = XmlFileLazyReader.new('C:\Users\iota_\Downloads\bioproject.xml', 'Package', 32768)
xml2json = BPXml2Jsonl.new('bioproject.json')
reader.each_element do |elm|
    xml2json.send(elm)
end
print Time.now, " Finished\n"
