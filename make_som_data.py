#文章を形態素解析して特定の品詞のみが含まれる配列にする
import MeCab
from sklearn.feature_extraction.text import CountVectorizer
import csv
import mojimoji
import yaml
csv.field_size_limit(1000000000)

with open("config.yaml") as f:
    config=yaml.safe_load(f)

#このサイトから取ってきた↓
#http://tyamagu2.xyz/articles/ja_text_classification/
class WordDividor:
    with open("config.yaml") as f:
        config=yaml.safe_load(f)
    INDEX_CATEGORY = 0
    INDEX_ROOT_FORM = 6
    #使用する品詞を変えたい場合はTARGET_CATEGORIESを変更する
    TARGET_CATEGORIES = config["TARGET_CATEGORIES"]
    EXCEPT_CATEGORIES = config["EXCLUDE_CATEGORIES"]

    def __init__(self, dictionary="mecabrc"):
        self.dictionary = dictionary
        self.tagger = MeCab.Tagger(self.dictionary)

    def extract_words(self, text):
        if not text:
            return []
        words = []
        node = self.tagger.parseToNode(text)
        while node:
            features = node.feature.split(',')
            if features[1] in self.EXCEPT_CATEGORIES or features[2] in self.EXCEPT_CATEGORIES:
                node = node.next
                continue
            if features[self.INDEX_CATEGORY] in self.TARGET_CATEGORIES:
                if features[self.INDEX_ROOT_FORM] == "*":
                    words.append(node.surface)
                else:
                    # prefer root form
                    words.append(features[self.INDEX_ROOT_FORM])
            node = node.next
        return words

def make_CountVectorizer(data):
    wd=WordDividor()
    cv=CountVectorizer(analyzer=wd.extract_words)
    counts=cv.fit_transform(data)

    #単語リストの出力
    D=cv.vocabulary_
    word_list=[]
    for i in D.keys():
        word_list.append(i+","+str(D[i])+"\n")

    with open(config["wordlist_path"],mode="w") as f:
        f.writelines(word_list)
    return counts.toarray()

#CSVファイルから文章を取り出す
#sentence_index: 何列目に文章があるか
#label_index: 引っ張りたいラベルが何列目か
#label_dict: 各ラベルに対して別の文字で割り当てたいときに辞書型で与える
def get_sentence(path,sentence_index,label_index,label_dict=None):
    #CSVの読み込み
    csv_file=open(path,"r",errors="",newline="")
    rawdata_L=csv.reader(csv_file,delimiter=",",doublequote=True,lineterminator="\r\n",quotechar='"',skipinitialspace=True)
    rawdata_L=list(rawdata_L)
    rawdata_L=[i for i in rawdata_L[1:]]

    #データとラベルに分離
    L=[]
    label=[]
    for i in rawdata_L:
        l=i[label_index].split(",")
        sentence=i[sentence_index]

        #ラベルを全角にする
        if config["label_to_zen"]:
            l=[mojimoji.han_to_zen(i) for i in l]

        #もともとラベルがない場合は無視する
        if len(l)==0:
            continue

        if label_dict is not None:
            l="".join(map(str,[label_dict[i] for i in l if i in label_dict]))

        if "その他" not in l and len(sentence)>0:
            L.append(mojimoji.han_to_zen(sentence))#ここで半角文字はすべて全角文字にしている
            label.append(l)

    return L,label

if __name__=="__main__":
    #大元のデータ
    path=config["data_path"]

    #タイトルによる自己組織化マップ生成
    data,label=get_sentence(path,config["sentence_index"],config["label_index"],config["label_dict"])

    counts=make_CountVectorizer(data)
    sum_L=[sum(i) for i in counts]
    for i in range(len(sum_L)):
        if sum_L[i]==0:
            print("zero",i,data[i])

    counts=[list(i/sum(i)) for i in counts]
    num=len(counts[0])

    for i in range(len(counts)):
        counts[i]=" ".join([f'{j:f}' for j in counts[i]])
        counts[i]+=" "+"".join(label[i])+"\n"
    counts=[str(num)+"\n"]+counts

    #ファイル書き込み
    print("writing...")
    with open(config["output_path"],mode="w") as f:
        f.writelines(counts)
    print("complete!")