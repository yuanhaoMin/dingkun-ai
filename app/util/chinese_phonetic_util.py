from xpinyin import Pinyin

MAX_DISTANCE = 3


class PyEditDistance:
    def __init__(self, data):
        self.data = data
        self.p = Pinyin()
        self.department_trie = self._build_trie([(department, department) for department in self.data.keys()])
        persons = [(person, person) for department, persons in self.data.items() for person in persons]
        self.person_trie = self._build_trie(persons)

    @staticmethod
    def _minimum(a, b, c):
        im = a if a < b else b
        return im if im < c else c

    def get_edit_distance(self, s, t):
        s = self.p.get_pinyin(s, ',', tone_marks='numbers')
        t = self.p.get_pinyin(t, ',', tone_marks='numbers')
        n = len(s)
        m = len(t)
        if n == 0:
            return m
        if m == 0:
            return n

        d = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            d[i][0] = i
        for j in range(m + 1):
            d[0][j] = j

        for i in range(1, n + 1):
            s_i = s[i - 1]
            for j in range(1, m + 1):
                t_j = t[j - 1]
                cost = 0 if s_i == t_j else 1
                d[i][j] = self._minimum(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)

        return d[n][m]

    class _TrieNode:
        def __init__(self):
            self.children = {}
            self.is_end_of_word = False
            self.value = None

    def _build_trie(self, items):
        root = self._TrieNode()
        for word, value in items:
            word_pinyin = self.p.get_pinyin(word, '', tone_marks='numbers')
            node = root
            for char in word_pinyin:
                if char not in node.children:
                    node.children[char] = self._TrieNode()
                node = node.children[char]
            node.is_end_of_word = True
            node.value = value
        return root

    def _search_within_distance(self, node, word, current_row, results):
        columns = len(word) + 1
        if node.is_end_of_word and current_row[-1] <= MAX_DISTANCE:
            results.append(node.value)

        for letter, child_node in node.children.items():
            next_row = [current_row[0] + 1]
            for col in range(1, columns):
                insert_cost = current_row[col] + 1
                delete_cost = next_row[col - 1] + 1
                replace_cost = current_row[col - 1]
                if word[col - 1] != letter:
                    replace_cost += 1
                next_row.append(min(insert_cost, delete_cost, replace_cost))
            self._search_within_distance(child_node, word, next_row, results)

    def _match_with_trie(self, target, trie):
        target_pinyin = self.p.get_pinyin(target, '', tone_marks='numbers')
        current_row = list(range(len(target_pinyin) + 1))
        results = []
        self._search_within_distance(trie, target_pinyin, current_row, results)
        return results

    def closest_match(self, target_list, actual):
        if not target_list:
            return None, float('inf')
        distances = [(item, self.get_edit_distance(item, actual)) for item in target_list]
        match, distance = min(distances, key=lambda x: x[1])
        return match, distance

    def get_relationship(self, department_name, person_name):
        matched_departments = self._match_with_trie(department_name, self.department_trie)
        matched_persons = self._match_with_trie(person_name, self.person_trie)

        closest_department, dep_distance = self.closest_match(matched_departments, department_name)
        closest_person, person_distance = self.closest_match(matched_persons, person_name)

        if closest_department and closest_person in self.data[closest_department]:
            return "受访部门存在，受访人存在", closest_department, dep_distance, closest_person, person_distance
        elif closest_department and closest_person:
            for department, persons in self.data.items():
                if closest_person in persons:
                    return "受访部门存在，受访人不对应", closest_department, dep_distance, closest_person, person_distance
            return "受访部门存在，受访人不存在", closest_department, dep_distance, None, float('inf')
        elif closest_department:
            return "受访部门存在，受访人不存在", closest_department, dep_distance, None, float('inf')
        elif closest_person:
            return "受访部门不存在，受访人存在", None, float('inf'), closest_person, person_distance
        else:
            return "受访部门不存在，受访人不存在", None, float('inf'), None, float('inf')

# if __name__ == '__main__':
#     data = {'领导层': ['李国军', '李瑛', '郑强', '周舒阳', '李浓新'],
#             '生产技术部': ['文继红', '邓丽娥', '赖世娣', '李爱红', '彭君婷', '郑泽斌', '刘传武', '陈钊', '候太华', '林建明', '杨洁', '张晓宁', '蔡佳娜', '黄志庭',
#                       '张烨', '梁柱艺', '莫水汉', '潘明优', '邱文强', '薛贵洪', '邹华', '郑强', '杨念', '钟杨林', '周俊光', '中控室'],
#             '实验室': ['文继红', '邓丽娥', '赖世娣', '李爱红', '彭君婷'], '工艺组': ['郑泽斌', '蔡佳娜', '周俊光'],
#             '设备组': ['刘传武', '陈钊', '候太华', '林建明', '杨洁', '张晓宁', '张烨'],
#             '运行班组': ['黄志庭', '梁柱艺', '莫水汉', '潘明优', '邱文强', '薛贵洪', '邹华', '杨念', '钟杨林', '中控室'],
#             '行政人事部': ['周舒阳', '赖斐', '刘诗媛', '周灵', '冯巧娜', '何雪求', '职安建测试人员'], '职安健': ['周灵', '何雪求', '职安建测试人员'],
#             '财务部': ['李瑛', '瞿天琼', '林子清'],
#             '长期承包商': ['李鑫', '曾凡东', '桂文生', '周玉盛', '于淑云', '曾美容', '钟任华', '郝春吉', '张汉武', '余惠琴', '胡志爱'],
#             '昱霖物业': ['李鑫', '曾凡东', '桂文生', '周玉盛', '于淑云', '曾美容', '钟任华', '郝春吉', '张汉武', '余惠琴', '胡志爱'], '短期承包商': []}
#     pyed = PyEditDistance(data)
#     result = pyed.get_relationship('领导层', '张总')
#     print(f"状态: {result[0]}, 部门: {result[1]} (距离: {result[2]}), 人员: {result[3]} (距离: {result[4]})")
#     print(pyed.get_edit_distance('生产技术', '生产技术部'))
