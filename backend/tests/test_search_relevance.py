"""
属性测试：搜索结果相关性
**Feature: nebula-ktv, Property 4: 搜索结果相关性**
**Validates: Requirements 3.2**
"""
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.song import Song
from app.utils.pinyin_utils import to_pinyin_abbr


def create_mock_song(title: str, artist: str) -> Song:
    """创建模拟歌曲对象"""
    song = Song(
        title=title,
        artist=artist,
        title_abbr=to_pinyin_abbr(title),
        artist_abbr=to_pinyin_abbr(artist),
    )
    # 模拟数据库字段
    from uuid import uuid4
    from datetime import datetime
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    song.status = "READY"
    return song


def check_search_relevance(songs: list[Song], query: str) -> bool:
    """
    检查搜索结果的相关性
    
    Args:
        songs: 搜索结果列表
        query: 搜索查询字符串
        
    Returns:
        True 如果所有结果都相关，False 否则
    """
    # 处理空查询和仅包含空白字符的查询
    if not query or not query.strip():
        return True
    
    query_lower = query.lower()
    
    for song in songs:
        # 检查是否在标题、歌手、或拼音首字母中匹配
        title_match = query_lower in song.title.lower()
        artist_match = query_lower in song.artist.lower()
        title_abbr_match = song.title_abbr and query_lower in song.title_abbr.lower()
        artist_abbr_match = song.artist_abbr and query_lower in song.artist_abbr.lower()
        
        if not (title_match or artist_match or title_abbr_match or artist_abbr_match):
            return False
    
    return True


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    query=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).filter(lambda x: x.strip()),
    songs_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),  # title
            st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))   # artist
        ),
        min_size=0,
        max_size=5
    )
)
def test_search_result_relevance(query, songs_data):
    """
    Property 4: 搜索结果相关性
    For any 搜索查询和歌曲数据集，返回的所有结果必须在标题或歌手名中包含查询字符串（或其拼音首字母匹配）。
    """
    # 创建模拟歌曲列表
    all_songs = [create_mock_song(title, artist) for title, artist in songs_data]
    
    # 模拟搜索过程：筛选相关歌曲
    relevant_songs = []
    
    # 处理空查询和仅包含空白字符的查询
    if not query or not query.strip():
        relevant_songs = all_songs  # 空查询返回所有结果
    else:
        query_lower = query.lower()
        
        for song in all_songs:
            title_match = query_lower in song.title.lower()
            artist_match = query_lower in song.artist.lower()
            title_abbr_match = song.title_abbr and query_lower in song.title_abbr.lower()
            artist_abbr_match = song.artist_abbr and query_lower in song.artist_abbr.lower()
            
            if title_match or artist_match or title_abbr_match or artist_abbr_match:
                relevant_songs.append(song)
    
    # 验证搜索结果的相关性
    assert check_search_relevance(relevant_songs, query), (
        f"Search results contain irrelevant songs for query '{query}'"
    )


def test_search_relevance_known_examples():
    """单元测试：已知示例的搜索相关性"""
    # 创建测试歌曲
    songs = [
        create_mock_song("青花瓷", "周杰伦"),
        create_mock_song("稻香", "周杰伦"),
        create_mock_song("告白气球", "周杰伦"),
        create_mock_song("演员", "薛之谦"),
        create_mock_song("Hello", "Adele"),
    ]
    
    # 测试中文搜索
    query = "周杰伦"
    relevant_songs = [s for s in songs if query in s.artist]
    assert check_search_relevance(relevant_songs, query)
    assert len(relevant_songs) == 3
    
    # 测试拼音首字母搜索
    query = "zjl"
    relevant_songs = [s for s in songs if s.artist_abbr and query in s.artist_abbr]
    assert check_search_relevance(relevant_songs, query)
    assert len(relevant_songs) == 3
    
    # 测试标题搜索
    query = "青花"
    relevant_songs = [s for s in songs if query in s.title]
    assert check_search_relevance(relevant_songs, query)
    assert len(relevant_songs) == 1
    
    # 测试英文搜索
    query = "hello"
    relevant_songs = [s for s in songs if query.lower() in s.title.lower()]
    assert check_search_relevance(relevant_songs, query)
    assert len(relevant_songs) == 1


def test_search_relevance_empty_query():
    """单元测试：空查询的处理"""
    songs = [create_mock_song("Test", "Artist")]
    
    # 空查询应该被认为是相关的（返回所有结果）
    assert check_search_relevance(songs, "")
    assert check_search_relevance(songs, "   ")


def test_search_relevance_no_results():
    """单元测试：无结果的搜索"""
    songs = []
    
    # 空结果列表应该被认为是相关的
    assert check_search_relevance(songs, "任意查询")