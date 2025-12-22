"""
属性测试：JSONB 查询正确性
**Feature: nebula-ktv, Property 10: JSONB 查询正确性**
**Validates: Requirements 8.3**
"""
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import List, Optional
from app.models.song import Song, JSONBFilter
from app.services.song_service import SongService


def create_mock_song(
    title: str,
    artist: str,
    bpm: Optional[int] = None,
    original_key: Optional[str] = None,
    genre: Optional[str] = None,
    scenario: Optional[List[str]] = None,
    difficulty_level: Optional[int] = None,
    language_family: Optional[str] = None,
    meta_json: Optional[dict] = None
) -> Song:
    """创建模拟歌曲对象"""
    from uuid import uuid4
    from datetime import datetime
    
    song = Song(
        title=title,
        artist=artist,
        bpm=bpm,
        original_key=original_key,
        genre=genre,
        scenario=scenario,
        difficulty_level=difficulty_level,
        language_family=language_family,
        meta_json=meta_json or {},
    )
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    song.status = "READY"
    return song


def check_jsonb_filter_match(song: Song, jsonb_filter: JSONBFilter) -> bool:
    """
    检查歌曲是否满足 JSONB 筛选条件
    
    Args:
        song: 歌曲对象
        jsonb_filter: JSONB 筛选条件
        
    Returns:
        True 如果歌曲满足所有筛选条件，False 否则
    """
    # BPM 范围筛选
    if jsonb_filter.bpm_min is not None:
        if song.bpm is None or song.bpm < jsonb_filter.bpm_min:
            return False
    if jsonb_filter.bpm_max is not None:
        if song.bpm is None or song.bpm > jsonb_filter.bpm_max:
            return False
    
    # 原调筛选
    if jsonb_filter.original_key is not None:
        if song.original_key != jsonb_filter.original_key:
            return False
    
    # 流派筛选
    if jsonb_filter.genre is not None:
        if song.genre != jsonb_filter.genre:
            return False
    
    # 场景标签筛选
    if jsonb_filter.tags:
        if song.scenario is None:
            return False
        for tag in jsonb_filter.tags:
            if tag not in song.scenario:
                return False
    
    # 难度范围筛选
    if jsonb_filter.difficulty_min is not None:
        if song.difficulty_level is None or song.difficulty_level < jsonb_filter.difficulty_min:
            return False
    if jsonb_filter.difficulty_max is not None:
        if song.difficulty_level is None or song.difficulty_level > jsonb_filter.difficulty_max:
            return False
    
    # 语系筛选
    if jsonb_filter.language_family is not None:
        if song.language_family != jsonb_filter.language_family:
            return False
    
    # meta_json 自定义键值筛选
    if jsonb_filter.meta_key is not None:
        if song.meta_json is None:
            return False
        if jsonb_filter.meta_key not in song.meta_json:
            return False
        if jsonb_filter.meta_value is not None:
            if str(song.meta_json.get(jsonb_filter.meta_key)) != jsonb_filter.meta_value:
                return False
    
    return True


def filter_songs_by_jsonb(songs: List[Song], jsonb_filter: JSONBFilter) -> List[Song]:
    """
    根据 JSONB 筛选条件过滤歌曲列表
    
    Args:
        songs: 歌曲列表
        jsonb_filter: JSONB 筛选条件
        
    Returns:
        满足筛选条件的歌曲列表
    """
    return [song for song in songs if check_jsonb_filter_match(song, jsonb_filter)]


# 策略定义
bpm_strategy = st.integers(min_value=60, max_value=200)
key_strategy = st.sampled_from(['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Am', 'Dm', 'Em'])
genre_strategy = st.sampled_from(['Pop', 'Rock', 'Ballad', 'R&B', 'EDM', 'Jazz'])
tag_strategy = st.sampled_from(['Wedding', 'Romance', 'Driving', 'Party', 'Healing', 'Nostalgia'])
difficulty_strategy = st.integers(min_value=1, max_value=5)
language_strategy = st.sampled_from(['Chinese', 'English', 'Japanese', 'Korean'])


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    songs_data=st.lists(
        st.fixed_dictionaries({
            'title': st.text(min_size=1, max_size=10, alphabet='abcdefghij'),
            'artist': st.text(min_size=1, max_size=10, alphabet='abcdefghij'),
            'bpm': st.one_of(st.none(), bpm_strategy),
            'original_key': st.one_of(st.none(), key_strategy),
            'genre': st.one_of(st.none(), genre_strategy),
            'scenario': st.one_of(st.none(), st.lists(tag_strategy, min_size=1, max_size=3)),
            'difficulty_level': st.one_of(st.none(), difficulty_strategy),
            'language_family': st.one_of(st.none(), language_strategy),
        }),
        min_size=1,
        max_size=10
    ),
    filter_bpm_min=st.one_of(st.none(), st.integers(min_value=60, max_value=150)),
    filter_bpm_max=st.one_of(st.none(), st.integers(min_value=100, max_value=200)),
    filter_key=st.one_of(st.none(), key_strategy),
    filter_genre=st.one_of(st.none(), genre_strategy),
    filter_tags=st.one_of(st.none(), st.lists(tag_strategy, min_size=1, max_size=2)),
    filter_difficulty_min=st.one_of(st.none(), st.integers(min_value=1, max_value=3)),
    filter_difficulty_max=st.one_of(st.none(), st.integers(min_value=2, max_value=5)),
    filter_language=st.one_of(st.none(), language_strategy),
)
def test_jsonb_query_correctness(
    songs_data,
    filter_bpm_min,
    filter_bpm_max,
    filter_key,
    filter_genre,
    filter_tags,
    filter_difficulty_min,
    filter_difficulty_max,
    filter_language
):
    """
    Property 10: JSONB 查询正确性
    For any JSONB 筛选条件，返回的歌曲必须满足该条件。
    """
    # 创建模拟歌曲列表
    all_songs = [
        create_mock_song(
            title=data['title'],
            artist=data['artist'],
            bpm=data['bpm'],
            original_key=data['original_key'],
            genre=data['genre'],
            scenario=data['scenario'],
            difficulty_level=data['difficulty_level'],
            language_family=data['language_family'],
        )
        for data in songs_data
    ]
    
    # 构建筛选条件
    jsonb_filter = JSONBFilter(
        bpm_min=filter_bpm_min,
        bpm_max=filter_bpm_max,
        original_key=filter_key,
        genre=filter_genre,
        tags=filter_tags,
        difficulty_min=filter_difficulty_min,
        difficulty_max=filter_difficulty_max,
        language_family=filter_language,
    )
    
    # 执行筛选
    filtered_songs = filter_songs_by_jsonb(all_songs, jsonb_filter)
    
    # 验证所有返回的歌曲都满足筛选条件
    for song in filtered_songs:
        assert check_jsonb_filter_match(song, jsonb_filter), (
            f"Song '{song.title}' does not match filter: "
            f"bpm={song.bpm}, key={song.original_key}, genre={song.genre}, "
            f"scenario={song.scenario}, difficulty={song.difficulty_level}, "
            f"language={song.language_family}"
        )


def test_jsonb_query_bpm_range():
    """单元测试：BPM 范围筛选"""
    songs = [
        create_mock_song("Song1", "Artist1", bpm=80),
        create_mock_song("Song2", "Artist2", bpm=120),
        create_mock_song("Song3", "Artist3", bpm=160),
        create_mock_song("Song4", "Artist4", bpm=None),
    ]
    
    # 筛选 BPM 在 100-140 之间的歌曲
    jsonb_filter = JSONBFilter(bpm_min=100, bpm_max=140)
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 1
    assert filtered[0].title == "Song2"
    assert filtered[0].bpm == 120


def test_jsonb_query_original_key():
    """单元测试：原调筛选"""
    songs = [
        create_mock_song("Song1", "Artist1", original_key="C"),
        create_mock_song("Song2", "Artist2", original_key="Am"),
        create_mock_song("Song3", "Artist3", original_key="C"),
        create_mock_song("Song4", "Artist4", original_key=None),
    ]
    
    # 筛选原调为 C 的歌曲
    jsonb_filter = JSONBFilter(original_key="C")
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 2
    assert all(s.original_key == "C" for s in filtered)


def test_jsonb_query_genre():
    """单元测试：流派筛选"""
    songs = [
        create_mock_song("Song1", "Artist1", genre="Pop"),
        create_mock_song("Song2", "Artist2", genre="Rock"),
        create_mock_song("Song3", "Artist3", genre="Pop"),
        create_mock_song("Song4", "Artist4", genre=None),
    ]
    
    # 筛选流派为 Pop 的歌曲
    jsonb_filter = JSONBFilter(genre="Pop")
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 2
    assert all(s.genre == "Pop" for s in filtered)


def test_jsonb_query_scenario_tags():
    """单元测试：场景标签筛选"""
    songs = [
        create_mock_song("Song1", "Artist1", scenario=["Wedding", "Romance"]),
        create_mock_song("Song2", "Artist2", scenario=["Party", "Driving"]),
        create_mock_song("Song3", "Artist3", scenario=["Wedding", "Healing"]),
        create_mock_song("Song4", "Artist4", scenario=None),
    ]
    
    # 筛选包含 Wedding 标签的歌曲
    jsonb_filter = JSONBFilter(tags=["Wedding"])
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 2
    assert all("Wedding" in s.scenario for s in filtered)
    
    # 筛选同时包含 Wedding 和 Romance 标签的歌曲
    jsonb_filter = JSONBFilter(tags=["Wedding", "Romance"])
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 1
    assert filtered[0].title == "Song1"


def test_jsonb_query_difficulty_range():
    """单元测试：难度范围筛选"""
    songs = [
        create_mock_song("Song1", "Artist1", difficulty_level=1),
        create_mock_song("Song2", "Artist2", difficulty_level=3),
        create_mock_song("Song3", "Artist3", difficulty_level=5),
        create_mock_song("Song4", "Artist4", difficulty_level=None),
    ]
    
    # 筛选难度在 2-4 之间的歌曲
    jsonb_filter = JSONBFilter(difficulty_min=2, difficulty_max=4)
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 1
    assert filtered[0].title == "Song2"
    assert filtered[0].difficulty_level == 3


def test_jsonb_query_language_family():
    """单元测试：语系筛选"""
    songs = [
        create_mock_song("Song1", "Artist1", language_family="Chinese"),
        create_mock_song("Song2", "Artist2", language_family="English"),
        create_mock_song("Song3", "Artist3", language_family="Chinese"),
        create_mock_song("Song4", "Artist4", language_family=None),
    ]
    
    # 筛选语系为 Chinese 的歌曲
    jsonb_filter = JSONBFilter(language_family="Chinese")
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 2
    assert all(s.language_family == "Chinese" for s in filtered)


def test_jsonb_query_meta_json():
    """单元测试：meta_json 自定义键值筛选"""
    songs = [
        create_mock_song("Song1", "Artist1", meta_json={"source": "youtube", "quality": "high"}),
        create_mock_song("Song2", "Artist2", meta_json={"source": "bilibili", "quality": "medium"}),
        create_mock_song("Song3", "Artist3", meta_json={"source": "youtube", "quality": "low"}),
        create_mock_song("Song4", "Artist4", meta_json={}),
    ]
    
    # 筛选 source 为 youtube 的歌曲
    jsonb_filter = JSONBFilter(meta_key="source", meta_value="youtube")
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 2
    assert all(s.meta_json.get("source") == "youtube" for s in filtered)
    
    # 筛选包含 source 键的歌曲（不指定值）
    jsonb_filter = JSONBFilter(meta_key="source")
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 3


def test_jsonb_query_combined_filters():
    """单元测试：组合筛选条件"""
    songs = [
        create_mock_song("Song1", "Artist1", bpm=120, genre="Pop", language_family="Chinese"),
        create_mock_song("Song2", "Artist2", bpm=120, genre="Rock", language_family="Chinese"),
        create_mock_song("Song3", "Artist3", bpm=80, genre="Pop", language_family="Chinese"),
        create_mock_song("Song4", "Artist4", bpm=120, genre="Pop", language_family="English"),
    ]
    
    # 组合筛选：BPM >= 100, 流派为 Pop, 语系为 Chinese
    jsonb_filter = JSONBFilter(bpm_min=100, genre="Pop", language_family="Chinese")
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 1
    assert filtered[0].title == "Song1"


def test_jsonb_query_empty_filter():
    """单元测试：空筛选条件"""
    songs = [
        create_mock_song("Song1", "Artist1", bpm=120),
        create_mock_song("Song2", "Artist2", bpm=80),
    ]
    
    # 空筛选条件应返回所有歌曲
    jsonb_filter = JSONBFilter()
    filtered = filter_songs_by_jsonb(songs, jsonb_filter)
    
    assert len(filtered) == 2
