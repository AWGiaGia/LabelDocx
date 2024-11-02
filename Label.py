import json
from ReadToken import ParseTokens # [117, 556, '('] [<原始序号>, <新序号>, <字符>]
from ReadDocx import ParseDocx # ['FF0000', 'A'] [<颜色>, <字符>]
from copy import deepcopy
from Interval import parse_interval
import os

from tqdm import tqdm
import logging

# u should check 'warning.log' to avoid hidden bugs
# NOTE: The result is usable if and only if there is no ERROR message in warning.log
if os.path.exists('warning.log'):
    print("Delete existing warning.log...")
    os.remove('warning.log')
logging.basicConfig(filename='warning.log',level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')


# 将docx中标注的颜色涂到tokens对应的字符位置上
# 上色后： # [117, 556, '(', 'FF0000'] [<原始序号>, <新序号>, <字符>, <颜色>]
def color(section,parsed_tokens,parsed_docx):
    colored_parsed_tokens = deepcopy(parsed_tokens)
    idx_docx = 0
    idx_tokens = 3 # tokens的开头<s>不做匹配
    # 给开头的<s>涂黑色
    for i in range(3):
        colored_parsed_tokens[i].append(None)

    while idx_tokens < len(parsed_tokens):
        if idx_docx < len(parsed_docx) and parsed_tokens[idx_tokens][-1] == parsed_docx[idx_docx][-1]:
            colored_parsed_tokens[idx_tokens].append(parsed_docx[idx_docx][0]) # 匹配上的，按照对应字符上色
            idx_docx += 1
        else:
            colored_parsed_tokens[idx_tokens].append(None) # 未匹配上的，涂黑色

        idx_tokens += 1
    
    # 一般情况下，parsed_tokens比parsed_docx长，所以此时parsed_docx已经匹配完了
    # 但是考虑到tokens有时候会因为限长度而从中间截断，所以也有可能多出来的parsed_docx并未匹配完
    # 如果出现这种情况要慎重考虑，因为也有可能是存在未过滤的字符，导致parsed_docx不是parsed_tokens的子串
    # 因此会记录到日志中，以便检查
    if idx_docx < len(parsed_docx):
        parsed_docx_str = ''
        for c in parsed_docx:
            parsed_docx_str += c[-1]
        
        parsed_tokens_str = ''
        for c in parsed_tokens:
            parsed_tokens_str += c[-1]

        diff_str = ''
        for c in parsed_docx[idx_docx:]:
            diff_str += c[-1]

        logging.warning(f"data item ({section}): The parsed_docx is not the substring of parsed_tokens")
        logging.info(f"parsed_docx is: {parsed_docx_str}")
        logging.info("#"*25)
        logging.info(f"parsed_tokens is: {parsed_tokens_str}")
        logging.info("#"*25)
        logging.info(f"The unmatched substring is: {diff_str}")

    return colored_parsed_tokens
    


# 根据颜色，为输入的tokens做分类
# 上色后： # [117, 556, '(', 'FF0000'] [<所属token序号>, <新序号>, <字符>, <颜色>]
# 返回一个字典，{<color>: [st_idx1,end_idx1,st_idx2,end_idx2,...st_idxn,end_idxn]}
def get_all_category(section,colored_list,ori_token):
    ignore_list = [" ", "\n", "\t", ",", "\'", "\"", "\\", "`", "\""]
    category_dict = {}
    i = 0

    # 将token按照颜色分类
    while (i < len(colored_list)):
        j = i
        while (j < len(colored_list) and colored_list[j][0] == colored_list[i][0]):
            if (colored_list[j][-1] != colored_list[i][-1]) and (colored_list[j][-2] not in ignore_list) and (colored_list[i][-2] not in ignore_list): # 一个token两种颜色（特殊分隔符号类的token不做考虑）
                idxed_ori_token = [[i,ori_token[i]] for i in range(len(ori_token))]

                logging.error(f"(section {section}) Conflicting token categories in '{ori_token[colored_list[i][0]]}' ({colored_list[i][0]})\n ori_token:{idxed_ori_token}")
                
                # raise ValueError(f"(section {section}) Conflicting token categories in '{ori_token[colored_list[i][0]]}' ({colored_list[i][0]})\n ori_token:{idxed_ori_token}")
            j += 1

        if colored_list[i][-1] != None:
            if colored_list[i][-1] in category_dict:
                category_dict[colored_list[i][-1]].append(colored_list[i][0])
            else:
                category_dict[colored_list[i][-1]] = [colored_list[i][0]]

        i = j

    # 将相邻的tokens用 '[起始token_id, 终止token_id]' 的形式表示
    for color in category_dict:
        category_dict[color] = parse_interval(category_dict[color])
    
    return category_dict


def label(section,colored_code,colored_doc,ori_code_token, ori_doc_token):
    result = {}
    code_category = get_all_category(section,colored_code,ori_code_token)
    doc_category = get_all_category(section,colored_doc,ori_doc_token)

    result['idx'] = section
    result['match'] = []

    for color in doc_category:
        if color in code_category:
            result['match'].append([doc_category[color],code_category[color]])


    return result

def main():
    SAVE_PATH = 'ljw.json'
    result = []

    labeled_docx_file = 'ljw.docx'
    tokenized_code_tokens_file = 'tokenized_code_tokens_train.json'
    tokenized_comment_tokens_file = 'tokenized_comment_tokens_train.json'

    parsed_tokens = ParseTokens(tokenized_code_tokens_file,tokenized_comment_tokens_file)
    docx_items = ParseDocx(labeled_docx_file)

    print("Start labeling...")
    for section, parsed_code_docx, parsed_doc_docx in tqdm(docx_items):
        parsed_code_token, parsed_doc_token, ori_code_token, ori_doc_token = parsed_tokens[section]

        colored_code = color(section,parsed_code_token, parsed_code_docx)
        colored_doc = color(section,parsed_doc_token, parsed_doc_docx)

        result.append(label(section,colored_code,colored_doc,ori_code_token, ori_doc_token))


    # 将每个字典序列化为 JSON 格式，并确保每个元素占用一行
    json_lines = [json.dumps(item) for item in result]

    # # 写入文件时，以 JSON 列表的格式写入
    # with open(SAVE_PATH, 'w') as f:
    #     f.write('[\n')
    #     f.write(',\n'.join(json_lines))
    #     f.write('\n]')

    with open(SAVE_PATH,'w') as f:
        for item in result:
            f.write(json.dumps(item) + '\n')
        # f.write(json.dumps(result))
    
    print(f"result saved in {SAVE_PATH}")

    
    warning = """
    You should check 'warning.log' to avoid hidden bugs\n
    NOTE: The result is usable if and only if there is no ERROR message in warning.log
    """

    print(warning)




if __name__ == '__main__':
    main()


# # 测试上色功能
# if __name__ == '__main__':

#     # parsed_tokens = ParseTokens('tokenized_code_tokens_train.json','tokenized_comment_tokens_train.json')
#     # parsed_code_token, parsed_doc_token, code_token, doc_token = parsed_tokens[13788]

#     # items = parse_docx('test.docx')

#     # for section, code, doc in items:
#     #     print(f"section number is: {section}")
#     #     print("Code Characters with Colors:", code)
#     #     print('='*50)
#     #     print("Documentation Characters with Colors:", doc)


#     docx_items = ParseDocx('label1029.docx')
#     parsed_tokens = ParseTokens('tokenized_code_tokens_train.json','tokenized_comment_tokens_train.json')

#     print("Start labeling...")
#     for section, parsed_code_docx, parsed_doc_docx in tqdm(docx_items):
#         parsed_code_token, parsed_doc_token, code_token, doc_token = parsed_tokens[section]

#         # if section in [198172,41532,147687,113803,121017,167917,58068,192571,199547]:
#         #     continue


#         try:
#             color(section,parsed_code_token, parsed_code_docx)
#         except:
#             print(f"Error while processing code ({section})")
        
#             op = ''
#             for c in parsed_code_docx:
#                 op += c[-1]
#             print(f"Here parsed_code_docx: {op}")

#             op = ''
#             for c in parsed_code_token:
#                 op += c[-1]
#             print(f"Here parsed_code_token: {op}")

#             raise ValueError(f"Here section: {section}")


#         try:
#             color(section,parsed_doc_token, parsed_doc_docx)
#         except:
#             print(f"Error while processing doc ({section})")

#             op = ''
#             for c in parsed_doc_docx:
#                 op += c[-1]
#             print(f"Here parsed_doc_docx: {op}")

#             op = ''
#             for c in parsed_doc_token:
#                 op += c[-1]
#             print(f"Here parsed_doc_token: {op}")

#             raise ValueError(f"Here section: {section}")