"""
属性测试：歌曲数据持久化 Round-Trip
**Feature: nebula-ktv, Property 1: 歌曲数据持久化 Round-Trip**
**Validates: Requirements 8.1**
"""
import pytest
import string
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.song import SongCreate, SongResponse, Song
from app.utils.pinyin_utils import to_pinyin_abbr, to_pinyin_full


# 定义简单的字符集，避免复杂的 Unicode 字符
SIMPLE_CHARS = string.ascii_letters + string.digits
CHINESE_SAMPLES = ["周杰伦", "林俊杰", "陈奕迅", "张学友", "刘德华", "青花瓷", "稻香", "晴天", "七里香", "告白气球"]
ALBUM_SAMPLES = ["七里香", "魔杰座", "十一月的萧邦", "范特西", "叶惠美"]
LYRICIST_SAMPLES = ["方文山", "周杰伦", "林夕", "黄伟文", None]
COMPOSER_SAMPLES = ["周杰伦", "林俊杰", "陈奕迅", None]


# 生成有效的歌曲数据策略 - 使用简单高效的策略
def song_create_strategy():
    """生成 SongCreate 数据的策略"""
    title_strategy = st.one_of(
        st.sampled_from(CHINESE_SAMPLES),
        st.text(alphabet=SIMPLE_CHARS, min_size=1, max_size=50)
    )
    artist_strategy = st.one_of(
        st.sampled_from(CHINESE_SAMPLES[:5]),
        st.text(alphabet=SIMPLE_CHARS, min_size=1, max_size=30)
    )
    
    return st.builds(
        SongCreate,
        title=title_strategy,
        artist=artist_strategy,
        subtitle=st.one_of(st.none(), st.text(alphabet=SIMPLE_CHARS, min_size=1, max_size=50)),
        album=st.one_of(st.none(), st.sampled_from(ALBUM_SAMPLES)),
        year=st.one_of(st.none(), st.integers(min_value=1980, max_value=2025)),
        lyricist=st.sampled_from(LYRICIST_SAMPLES),
        composer=st.sampled_from(COMPOSER_SAMPLES),
        language_family=st.one_of(st.none(), st.sampled_from(["Chinese", "English", "Japanese", "Korean"])),
        language_dialect=st.one_of(st.none(), st.sampled_from(["Mandarin", "Cantonese", "Hokkien"])),
        singing_type=st.one_of(st.none(), st.sampled_from(["Solo", "Duet", "Group", "Choir"])),
        gender_type=st.one_of(st.none(), st.sampled_from(["Male", "Female", "Mix", "Band"])),
        genre=st.one_of(st.none(), st.sampled_from(["Pop", "Rock", "R&B", "Ballad", "EDM"])),
        scenario=st.one_of(st.none(), st.lists(st.sampled_from(["Wedding", "Driving", "Breakup", "Party"]), max_size=3)),
        meta_json=st.fixed_dictionaries({}, optional={
            "bpm": st.integers(min_value=60, max_value=200),
            "key": st.sampled_from(["C", "D", "E", "F", "G", "A", "B", "Cm", "Dm", "Em"]),
        })
    )


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(song_data=song_create_strategy())
def test_song_data_persistence_roundtrip(song_data):
    """
    Property 1: 歌曲数据持久化 Round-Trip
    For any 有效的歌曲数据，创建歌曲后查询应返回等价的数据对象。
    
    注意：由于没有实际数据库连接，这里测试数据模型的序列化/反序列化一致性
    """
    from uuid import uuid4
    from datetime import datetime
    
    # 1. 创建 Song 对象（模拟数据库插入）
    song = Song(
        # 基础信息
        title=song_data.title,
        artist=song_data.artist,
        subtitle=song_data.subtitle,
        album=song_data.album,
        year=song_data.year,
        
        # 创作信息
        lyricist=song_data.lyricist,
        composer=song_data.composer,
        
        # 分类信息
        language_family=song_data.language_family,
        language_dialect=song_data.language_dialect,
        singing_type=song_data.singing_type,
        gender_type=song_data.gender_type,
        genre=song_data.genre,
        scenario=song_data.scenario,
        
        # 搜索优化
        title_pinyin=to_pinyin_full(song_data.title),
        title_abbr=to_pinyin_abbr(song_data.title),
        artist_pinyin=to_pinyin_full(song_data.artist),
        artist_abbr=to_pinyin_abbr(song_data.artist),
        
        # 兜底字段
        meta_json=song_data.meta_json,
    )
    
    # 模拟数据库自动生成的字段
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    song.status = "PENDING"
    song.play_count = 0
    song.is_favorite = False
    
    # 2. 转换为响应对象（模拟数据库查询）
    response = SongResponse.model_validate(song)
    
    # 3. 验证 Round-Trip 一致性 - 基础信息
    assert response.title == song_data.title
    assert response.artist == song_data.artist
    assert response.subtitle == song_data.subtitle
    assert response.album == song_data.album
    assert response.year == song_data.year
    
    # 验证创作信息
    assert response.lyricist == song_data.lyricist
    assert response.composer == song_data.composer
    
    # 验证分类信息
    assert response.language_family == song_data.language_family
    assert response.language_dialect == song_data.language_dialect
    assert response.singing_type == song_data.singing_type
    assert response.gender_type == song_data.gender_type
    assert response.genre == song_data.genre
    assert response.scenario == song_data.scenario
    
    # 验证自动生成的拼音
    assert response.title_abbr == to_pinyin_abbr(song_data.title)
    assert response.artist_abbr == to_pinyin_abbr(song_data.artist)
    assert response.title_pinyin == to_pinyin_full(song_data.title)
    assert response.artist_pinyin == to_pinyin_full(song_data.artist)
    
    # 验证兜底字段
    assert response.meta_json == song_data.meta_json
    
    # 验证必需字段存在
    assert response.id is not None
    assert response.status is not None
    assert response.created_at is not None
    assert response.updated_at is not None


def test_song_persistence_known_examples():
    """单元测试：已知示例的持久化 - 完整元数据"""
    from uuid import uuid4
    from datetime import datetime
    
    song_data = SongCreate(
        title="青花瓷",
        artist="周杰伦",
        subtitle=None,
        album="我很忙",
        year=2007,
        lyricist="方文山",
        composer="周杰伦",
        language_family="Chinese",
        language_dialect="Mandarin",
        singing_type="Solo",
        gender_type="Male",
        genre="Pop",
        scenario=["Wedding", "Romance"],
        meta_json={"bpm": 120, "key": "C"}
    )
    
    song = Song(
        title=song_data.title,
        artist=song_data.artist,
        subtitle=song_data.subtitle,
        album=song_data.album,
        year=song_data.year,
        lyricist=song_data.lyricist,
        composer=song_data.composer,
        language_family=song_data.language_family,
        language_dialect=song_data.language_dialect,
        singing_type=song_data.singing_type,
        gender_type=song_data.gender_type,
        genre=song_data.genre,
        scenario=song_data.scenario,
        title_pinyin=to_pinyin_full(song_data.title),
        title_abbr=to_pinyin_abbr(song_data.title),
        artist_pinyin=to_pinyin_full(song_data.artist),
        artist_abbr=to_pinyin_abbr(song_data.artist),
        meta_json=song_data.meta_json,
    )
    
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    song.status = "PENDING"
    song.play_count = 0
    song.is_favorite = False
    
    response = SongResponse.model_validate(song)
    
    # 验证基础信息
    assert response.title == "青花瓷"
    assert response.artist == "周杰伦"
    assert response.album == "我很忙"
    assert response.year == 2007
    
    # 验证创作信息
    assert response.lyricist == "方文山"
    assert response.composer == "周杰伦"
    
    # 验证分类信息
    assert response.language_family == "Chinese"
    assert response.language_dialect == "Mandarin"
    assert response.singing_type == "Solo"
    assert response.gender_type == "Male"
    assert response.genre == "Pop"
    assert response.scenario == ["Wedding", "Romance"]
    
    # 验证拼音
    assert response.title_abbr == "qhc"
    assert response.artist_abbr == "zjl"
    assert response.title_pinyin == "qing hua ci"
    assert response.artist_pinyin == "zhou jie lun"
    
    # 验证兜底字段
    assert response.meta_json == {"bpm": 120, "key": "C"}


def test_song_persistence_duet_song():
    """单元测试：对唱歌曲的持久化"""
    from uuid import uuid4
    from datetime import datetime
    
    song_data = SongCreate(
        title="屋顶",
        artist="周杰伦/温岚",
        album="温岚同名专辑",
        year=2000,
        lyricist="周杰伦",
        composer="周杰伦",
        language_family="Chinese",
        language_dialect="Mandarin",
        singing_type="Duet",
        gender_type="Mix",
        genre="Ballad",
        scenario=["Romance", "Duet"],
        meta_json={}
    )
    
    song = Song(
        title=song_data.title,
        artist=song_data.artist,
        album=song_data.album,
        year=song_data.year,
        lyricist=song_data.lyricist,
        composer=song_data.composer,
        language_family=song_data.language_family,
        language_dialect=song_data.language_dialect,
        singing_type=song_data.singing_type,
        gender_type=song_data.gender_type,
        genre=song_data.genre,
        scenario=song_data.scenario,
        title_pinyin=to_pinyin_full(song_data.title),
        title_abbr=to_pinyin_abbr(song_data.title),
        artist_pinyin=to_pinyin_full(song_data.artist),
        artist_abbr=to_pinyin_abbr(song_data.artist),
        meta_json=song_data.meta_json,
    )
    
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    song.status = "READY"
    song.play_count = 0
    song.is_favorite = False
    
    response = SongResponse.model_validate(song)
    
    # 验证对唱歌曲特有字段
    assert response.singing_type == "Duet"
    assert response.gender_type == "Mix"
    assert "Duet" in response.scenario


def test_song_persistence_empty_meta_json():
    """单元测试：空 meta_json 的处理"""
    from uuid import uuid4
    from datetime import datetime
    
    song_data = SongCreate(
        title="Test Song",
        artist="Test Artist"
    )
    
    song = Song(
        title=song_data.title,
        artist=song_data.artist,
        meta_json=song_data.meta_json,
        title_pinyin=to_pinyin_full(song_data.title),
        title_abbr=to_pinyin_abbr(song_data.title),
        artist_pinyin=to_pinyin_full(song_data.artist),
        artist_abbr=to_pinyin_abbr(song_data.artist),
    )
    
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    song.status = "PENDING"
    song.play_count = 0
    song.is_favorite = False
    
    response = SongResponse.model_validate(song)
    
    assert response.meta_json == {}
    assert response.album is None
    assert response.lyricist is None
    assert response.scenario is None
