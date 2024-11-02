import json
from tqdm import tqdm

class ParseTokens:
    def __init__(self,code_file_path,doc_file_path):
        self.code_token_list = []
        self.doc_token_list = []

        print(f'Loading code tokens...')
        with open(code_file_path,'r') as f:
            self.code_token_list = json.loads(f.read())
            for i in tqdm(range(len(self.code_token_list))):
                self.code_token_list[i] = [token.replace('Ġ', '') for token in self.code_token_list[i]]
            # for line in tqdm(f):
            #     data_item = json.loads(line)
            #     self.code_token_list.append(data_item)

        print(f'Loading doc tokens...')
        with open(doc_file_path,'r') as f:
            self.doc_token_list = json.loads(f.read())
            for i in tqdm(range(len(self.doc_token_list))):
                self.doc_token_list[i] = [token.replace('Ġ', '') for token in self.doc_token_list[i]]
            # for line in tqdm(f):
            #     data_item = json.loads(line)
            #     self.doc_token_list.append(data_item)

    def split_and_label(self,token_list):
        res = []
        new_idx = 0
        for ori_idx in range(len(token_list)):
            token = token_list[ori_idx]
            for c in token:
                res.append([ori_idx,new_idx, c])
                new_idx += 1
        
        return res

    def __getitem__(self,idx):
        code_token = self.code_token_list[idx]
        doc_token = self.doc_token_list[idx]
        parsed_code_token = self.split_and_label(code_token)
        parsed_doc_token = self.split_and_label(doc_token)

        return parsed_code_token, parsed_doc_token, code_token, doc_token


# def parse_tokens(file_path):
#     items = []
#     with open(file_path,'r') as f:
#         for line in f:
#             data_item = json.loads(line)
#             parsed_code_token = split_and_label(data_item['code_tokens'])
#             parsed_doc_token = split_and_label(data_item['docstring_tokens'])

#             items.append([parsed_code_token,parsed_doc_token])
    
#     return items


# 输入原始的token列表，返回带在原始token列表中的索引位置的字符索引列表
# 每个数据项的形式： [原始idx，<字符>]





if __name__ == '__main__':
    parsed_tokens = ParseTokens('tokenized_code_tokens_train.json','tokenized_comment_tokens_train.json')
    parsed_code_token, parsed_doc_token, code_token, doc_token = parsed_tokens[13788]

    print(parsed_doc_token)

    print('='*50)

    print(doc_token)