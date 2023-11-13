import json
import collections.abc

def is_array(o):
    return isinstance(o, collections.abc.Sequence) and not isinstance(o, str)

def generate_api_markdown(api_json_file, markdown_file):
    with open(api_json_file, 'r') as f:
        api_json = json.load(f)

    md = open(markdown_file, 'w')

    def println(s):
        md.write(s)
        md.write('\n')

    def generate_single_api(api_obj, level):
        println("{} {}\n".format('#' * level, api_obj.get("name", "Unnamed API")))
        println("```")
        println("{} {}".format(api_obj.get("method", "GET"), api_obj.get("url", "<error: no url>")))
        println("```\n")

        def process_request_response(r, desc, visible_cols=None):
            curr_obj = r
            curr_desc = desc
            tables = []
            desc_tables = []
            desc_table_names = []

            println("```json")
            println(json.dumps(r, ensure_ascii=False, indent=4))
            println('```\n')

            def travel_array(arr, name):
                nonlocal curr_desc, curr_obj
                curr_obj = arr[0]
                curr_desc = curr_desc[0]
                v = arr[0]
                if isinstance(v, dict):
                    travel_obj(v, name)
                if is_array(v):
                    travel_array(v, name)

            def travel_obj(obj, name):
                nonlocal curr_desc, curr_obj, desc_table_names
                tmp_desc = curr_desc
                tables.append(obj)
                desc_tables.append(tmp_desc)
                desc_table_names.append(name)
                for k, v in obj.items():
                    curr_obj = v
                    curr_desc = tmp_desc[k]
                    if isinstance(v, dict):
                        travel_obj(v, name='.'.join([name, k]))
                    if is_array(v):
                        travel_array(v, name='.'.join([name, k]))


            travel_obj(r, name="")
            print(tables)
            print(desc_tables)

            def generate_table(obj, desc, name):
                def filter_table_row(A):
                    if visible_cols is None:
                        return A
                    return [ x for i, x in enumerate(A) if visible_cols[i] ]

                def print_titles():
                    title = [ "名称", "类型", "必需", "默认值", "含义" ]
                    println('|{}|'.format('|'.join(filter_table_row(title))))
                    println('|{}|'.format('|'.join(filter_table_row(['----'] * title.__len__()))))

                def get_type_str(v):
                    if v is None:
                        return "any"
                    if isinstance(v, int):
                        return "int"
                    if isinstance(v, float):
                        return "float"
                    if isinstance(v, str):
                        return "string"
                    if isinstance(v, bool):
                        return "bool"
                    if isinstance(v, dict):
                        return "object"
                    if is_array(v):
                        return get_type_str(v[0]) + "[]"
                    return "unknown"

                def generate_value(v):
                    if is_array(v) or isinstance(v, dict):
                        return ""
                    return str(v)

                println('{}说明：\n'.format(name))
                print_titles()
                for i, (k, v) in enumerate(obj.items()):
                    name = k
                    typename = get_type_str(v)
                    required = not ('(optional)' in desc[k])
                    default_value = str(generate_value(v)) if not required else ' '
                    if isinstance(desc[k], str):
                        meaning = str(desc[k]).replace("(optional)", "").replace('|',',')
                    elif isinstance(desc[k], dict):
                        meaning = "<Object>"
                    elif is_array(desc[k]):
                        meaning = "见{}的说明".format(name)
                    else:
                        meaning = str(desc[k])
                    println('|{}|'.format('|'.join(filter_table_row([ s for s in [
                        name, typename, 'Yes' if required else 'No', default_value, meaning
                    ] ]))))
                println('\n')

            for obj, desc, name in zip(tables, desc_tables, desc_table_names):
                generate_table(obj, desc, name)
            println('\n\n')

        println('* **请求**\n')
        process_request_response(api_obj.get("request", {}),
                                 api_obj.get("request_description", {}))

        println('* **响应**\n')
        process_request_response(api_obj.get("response", {}),
                                 api_obj.get("response_description", {}),
                                 visible_cols=[1, 1, 0, 0, 1])


    def process_api(api_arr, level):
        print(json.dumps(api_arr, ensure_ascii=False))
        for api in api_arr:
            generate_single_api(api, level)

    def generate_section(sections, level, section_ids):
        for sec_id, section in enumerate(sections):
            next_section_ids = [ *section_ids, str(sec_id + 1) ]
            println('{} {}. {}\n'.format('#' * level, '.'.join(next_section_ids),
                                        section.get("section", "No title")))

            if 'api' in section.keys():
                process_api(section["api"], level + 1)

            if 'subsections' in section.keys():
                generate_section(section['subsections'], level + 1, next_section_ids)


    generate_section(api_json, 2, section_ids=[])

    md.close()

if __name__ == '__main__':
    generate_api_markdown('api.json', 'api.md')

