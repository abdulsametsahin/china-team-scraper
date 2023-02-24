import re
import pymysql
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from config import mysql_config


class Translator:

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
        self.tokenizer.src_lang = "zh_Hans"
        while True:
            try:
                self.translate()
            except KeyboardInterrupt:
                print("[x] [Translate] Keyboard interrupt, exiting")
                exit()
            except Exception as e:
                print(f"[x] [Translate] Error: {e}")

    def split_text(self, text):
        text = text.split('\n')
        g = []
        for i in text:
            x = re.sub('\. ', '.\\n', i)
            x = re.sub('\t', '\\n', x)
            g.append(x.split('\n'))
        k = []
        for i in g:
            for j in i:
                k.append(j)
        return k

    def translate_zh_to_en(self, text):
        G = []
        l = self.split_text(text)

        for i in l:
            encoded_hi = self.tokenizer(i, return_tensors="pt")
            generated_tokens = self.model.generate(**encoded_hi,
                                                   max_new_tokens=200,
                                                   forced_bos_token_id=self.tokenizer.lang_code_to_id["eng_Latn"])
            article_en = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

            for n in article_en:
                G.append(n)
        return ' '.join(G)

    def translate(self):
        connection = pymysql.connect(host=mysql_config['host'], user=mysql_config['user'],
                                     password=mysql_config['password'],
                                     database=mysql_config['database'], port=mysql_config['port'])
        cursor = connection.cursor()
        sql = "SELECT * FROM `companies` WHERE `english_name` IS NULL LIMIT 1000"
        cursor.execute(sql)
        result = cursor.fetchall()

        if len(result) == 0:
            print("[x] [Translate] No more data to translate. Sleeping for 15 minutes")
            time.sleep(900)
            return

        for row in result:
            name = row[1]
            translated_name = self.translate_zh_to_en(name)
            sql = "UPDATE `companies` SET `english_name` = %s WHERE `id` = %s"
            cursor.execute(sql, (translated_name, row[0]))
            connection.commit()
