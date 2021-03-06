import sys, os, re, json

def get_xml_file(files):
    res = list()
    for file in files:
        if file.endswith(".xml"):
            res.append(file)
            #break
    return res

def get_file_content_into_string(directory, file):
    data = ""
    full_path = directory + "/" + file
    with open(full_path, 'r') as myfile:
        data=myfile.read().replace('\n', '')
    return data

def get_list_of_template_info(directory, xml_files):
    templates_info = list()
    for api_file in xml_files:
        file_content = get_file_content_into_string(directory, api_file)
        api_info = extract_info(file_content)
        templates_info.append(api_info)
    return templates_info

def get_name(match):
    name = re.search("name=\"(.*?)\"", match)
    return name.group(1)

def get_templates_by_resource(resource):
    templates_matches = re.findall("<call-template target=\"(.*?)\".*?/?>", resource)
    return templates_matches

def get_sequences_by_resource(resource):
    sequences_matches = re.findall("<sequence key=\"(.*?)\".*?/?>", resource)
    return sequences_matches

def get_endpoints_by_resource(resource):
    endpoints_matches = re.findall("<endpoint key=\"(.*?)\".*?/?>", resource)
    return endpoints_matches

def get_registers_by_resource(resource):
    registers_matches = re.findall("expression=\"get-property\('registry','(conf:/.*?)'\)\"", resource)
    return registers_matches

def get_stores_by_resource(resource):
    sources_matches = re.findall("<messageStore.*?name=\"(.*?)\".*?\/?>", resource)
    return sources_matches

def get_processor_by_resource(resource):
    processor_matches = re.findall("<messageProcessor.*?name=\"(.*?)\".*?\/?>", resource)
    return processor_matches

def get_resources(match):
    res_templates = list()
    res_templates_by_resource = list()
    res_sequences_by_resource = list()
    res_endpoints_by_resource = list()
    res_registers_by_resource = list()
    res_stores_by_resource = list()
    res_processor_by_resource = list()
    sequence = re.findall("<sequence>(.*?)</sequence>", match)
    for resource in sequence:
        uri_match = re.search("value=\"\[Template\](.*?)\"", resource)
        if uri_match:
            value = uri_match.group(1)
            #uri = remove_internal_if_exists(value)
            res_templates.append(value)
        res_templates_by_resource.append(get_templates_by_resource(resource))
        res_sequences_by_resource.append(get_sequences_by_resource(resource))
        res_endpoints_by_resource.append(get_endpoints_by_resource(resource))
        res_registers_by_resource.append(get_registers_by_resource(resource))
        res_stores_by_resource.append(get_stores_by_resource(resource))
        res_processor_by_resource.append(get_processor_by_resource(resource))
    return (res_templates, res_templates_by_resource, res_sequences_by_resource, res_endpoints_by_resource, res_registers_by_resource, res_stores_by_resource, res_processor_by_resource)

def extract_info(template_content):
    res = {
        'name':'',
        'context':'',
        'resources':[],
        'endpoints':{},
        'templates':{},
        'sequences':{},
        'registers':{},
        'stores':{},
        'processors':{}
    }

    matches = re.search("<template (.*?)>(.*?)</template>", template_content)
    if matches:
        res['name'] = get_name(matches.group(1))
        ttuple = get_resources(matches.group(2))
        res['resources'] = ttuple[0]
        template_dict = dict()
        sequence_dict = dict()
        endpoint_dict = dict()
        register_dict = dict()
        store_dict = dict()
        processor_dict = dict()
        for i in range(0, len(ttuple[0])):
            list_template = ttuple[1][i]
            if list_template and len(list_template)>0:
                template_dict[ttuple[0][i]] = list(set(list_template))
            list_sequence = ttuple[2][i]
            if list_sequence and len(list_sequence)>0:
                sequence_dict[ttuple[0][i]] = list(set(list_sequence))
            list_endpoint = ttuple[3][i]
            if list_endpoint and len(list_endpoint)>0:
                endpoint_dict[ttuple[0][i]] = list(set(list_endpoint))
            list_register = ttuple[4][i]
            if list_register and len(list_register)>0:
                register_dict[ttuple[0][i]] = list(set(list_register))
            list_store = ttuple[5][i]
            if list_store and len(list_store)>0:
                store_dict[ttuple[0][i]] = list(set(list_store))
            list_processor = ttuple[6][i]
            if list_processor and len(list_processor)>0:
                processor_dict[ttuple[0][i]] = list(set(list_processor))
        res['templates'] = template_dict
        res['sequences'] = sequence_dict
        res['endpoints'] = endpoint_dict
        res['registers'] = register_dict
        res['stores'] = store_dict
        res['processors'] = processor_dict
        #print(res)
    return res

def save_object(obj, filename):
    with open(filename, 'w') as outfile:
        json.dump(obj, outfile)

def put_json_in_this_directory(apis_json):
    save_object(apis_json, "template_result.json")

if __name__ == '__main__':
    if len(sys.argv)>1:
        directory_path = sys.argv[1]
        if os.path.isdir(directory_path) and os.path.exists(directory_path):
            files = os.listdir(directory_path)
            if files and len(files)>0:
                xml_files = get_xml_file(files)
                apis_info = get_list_of_template_info(directory_path, xml_files)
                put_json_in_this_directory(apis_info)
            else:
                print("There are not any file in this directory")
        else:
            print("Argument is not a valid directory path")
    else:
        print("There are not arguments")