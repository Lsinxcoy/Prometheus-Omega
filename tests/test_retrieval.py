"""Retrieval模块测试"""
import sys
sys.path.insert(0, 'src')

from prometheus_omega.retrieval import Retrieval, SearchResult

def test_retrieval_search():
    """测试搜索"""
    r = Retrieval()
    results = r.search('query', top_k=10)
    assert isinstance(results, list)

def test_retrieval_query():
    """测试向量查询"""
    r = Retrieval()
    results = r.query([0.1]*128, k=5)
    assert isinstance(results, list)

def test_retrieval_index():
    """测试索引"""
    r = Retrieval()
    r.index_document('doc1', 'content')
    assert 'doc1' in r.index

if __name__ == '__main__':
    test_retrieval_search()
    test_retrieval_query()
    test_retrieval_index()
    print("✅ All Retrieval tests passed!")
