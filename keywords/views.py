from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import pandas as pd
from konlpy.tag import Kkma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import time
# Create your views here.


@api_view(['POST'])
def extraction(request):
    if request.method == 'POST':
        article = request.data['article']

        extraction = Keyword_extraction()

        keywords = extraction.extract_from_article(article)
        return Response(keywords)


class Keyword_extraction():
    def __init__(self):
        self.kkma = Kkma()

    def extract_from_article(self, article):
        start = time.time()

        df_stopwords = pd.read_excel(
            '/home/ubuntu/data//stop_words.xlsx', engine='openpyxl')

        stopwords = df_stopwords['형태'].tolist()

        # 글을 문장별로 구분
        sentences = self.get_sentences(article)
        # 문장별 명사 추출
        nouns = self.get_nouns(sentences, stopwords)
        # 문장별 키워드 추출
        keywords = self.get_keywords(nouns, 5)

        print("키워드 추출 시간(초) : ", time.time() - start)
        return keywords

    def tf_idf(self, sentences):
        # 문장을 넣으면 문장 단위로 tf-idf 수치를 벡터화
        vectorizer = TfidfVectorizer()
        tfidf_mat = vectorizer.fit_transform(sentences).toarray()

        graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)

        # 정수 인덱스 이름 불러오기
        # print(vectorizer.get_feature_names())

        return graph_sentence

    def cv(self, sentences):
        # 텍스트를 토큰 매트릭스로 변환
        #  token_pattern = r"(?u)\b\w+\b" 1개의 단어도 포함되도록
        cv = CountVectorizer(token_pattern=r"(?u)\b\w+\b")
        cv_mat = normalize(cv.fit_transform(
            sentences).toarray().astype(float), axis=0)

        vocab = cv.vocabulary_
        idx_to_word = {vocab[word]: word for word in vocab}
        graph_word = np.dot(cv_mat.T, cv_mat)

        return idx_to_word, graph_word

    def get_keywords(self, nouns, num):
        idx_to_word, graph_word = self.cv(nouns)
        ranks = self.get_ranks(graph_word)
        sort_ranks = sorted(ranks, key=lambda k: ranks[k], reverse=True)

        keywords = []
        index = []
        for idx in sort_ranks[:num]:
            index.append(idx)
        for idx in index:
            keywords.append(idx_to_word[idx])

        return keywords

    def get_ranks(self, graph, d=0.85):  # d = damping factor
        A = graph
        matrix_size = A.shape[0]
        for id in range(matrix_size):
            A[id, id] = 0
            col_sum = np.sum(A[:, id])  # A[:, id] = A[:][id]
            if col_sum != 0:
                A[:, id] /= col_sum
            A[:, id] *= -d
            A[id, id] = 1

        B = (1-d) * np.ones((matrix_size, 1))

        ranks = np.linalg.solve(A, B)  # 연립방적식 Ax = b
        return {idx: r[0] for idx, r in enumerate(ranks)}

    def get_sentences(self, text):
        sentences = self.kkma.sentences(text)
        return sentences

    def get_pos(self, sentences):
        for sentence in sentences:
            pos = self.kkma.pos(sentence)
            print(pos)

    def get_nouns(self, sentences, stopwords):
        nouns = []

        for sentence in sentences:
            if sentence is not '':
                pos = self.kkma.pos(sentence)
                noun = []
                for word in pos:
                    if (word[1] == 'NNG' or word[1] == 'NNP') and word[0] not in stopwords:
                        noun.append(word[0])

                if len(noun) > 0:
                    nouns.append(' '.join(noun))
        return nouns
