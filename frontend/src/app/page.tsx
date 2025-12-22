"use client";

/**
 * 首页资源库
 * 集成 SearchBar、RecentSection、SongList
 * Requirements: 3.1, 3.3, 3.4
 */

import * as React from "react";
import { SearchBar, RecentSection, SongList } from "@/components/library";
import {
  useSongs,
  useRecentSongs,
  useSearchSongs,
  isSongPlayable,
} from "@/hooks/use-songs";
import type { Song } from "@/lib/api";

export default function HomePage() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [showToast, setShowToast] = React.useState(false);
  const [toastMessage, setToastMessage] = React.useState("");

  // 数据获取
  const { songs: allSongs, loading: loadingAll, error: errorAll } = useSongs({ limit: 50 });
  const { songs: recentSongs, loading: loadingRecent } = useRecentSongs(10);
  const { songs: searchResults, loading: loadingSearch, search } = useSearchSongs(20);

  // 是否处于搜索模式
  const isSearching = searchQuery.trim().length > 0;

  // 显示的歌曲列表
  const displaySongs = isSearching ? searchResults : allSongs;
  const isLoading = isSearching ? loadingSearch : loadingAll;

  // 搜索处理
  const handleSearch = React.useCallback(
    (query: string) => {
      setSearchQuery(query);
      if (query.trim()) {
        search(query);
      }
    },
    [search]
  );

  // 播放歌曲
  const handlePlay = React.useCallback((song: Song) => {
    if (!isSongPlayable(song)) {
      // 显示 Toast 提示
      setToastMessage("AI 正在加工中，请稍候...");
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }
    // TODO: 跳转到播放器页面
    window.location.href = `/player/${song.id}`;
  }, []);

  // 点击歌曲
  const handleSongClick = React.useCallback((song: Song) => {
    if (!isSongPlayable(song)) {
      setToastMessage("AI 正在加工中，请稍候...");
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }
    // TODO: 跳转到播放器页面
    window.location.href = `/player/${song.id}`;
  }, []);

  return (
    <main className="min-h-screen bg-background safe-area-inset">
      <div className="mx-auto max-w-4xl px-4 py-6 space-y-8">
        {/* 页面标题 */}
        <h1 className="text-page-title text-text-main">星云 KTV</h1>

        {/* 搜索框 - Requirements: 3.1, 3.2 */}
        <SearchBar
          onSearch={handleSearch}
          placeholder="搜索歌曲或歌手..."
          loading={loadingSearch}
        />

        {/* 搜索模式下不显示最近添加 */}
        {!isSearching && (
          <RecentSection
            songs={recentSongs}
            loading={loadingRecent}
            onSongClick={handleSongClick}
          />
        )}

        {/* 歌曲列表 - Requirements: 3.4, 3.5 */}
        <section className="space-y-4">
          <h2 className="text-song-title text-text-main px-1">
            {isSearching ? `搜索结果` : "全部歌曲"}
          </h2>

          {errorAll && !isSearching && (
            <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20">
              <p className="text-song-meta text-destructive">
                加载失败: {errorAll}
              </p>
            </div>
          )}

          <SongList
            songs={displaySongs}
            loading={isLoading}
            onPlay={handlePlay}
            onSongClick={handleSongClick}
            emptyText={isSearching ? "未找到匹配的歌曲" : "暂无歌曲"}
          />
        </section>
      </div>

      {/* Toast 提示 */}
      {showToast && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 animate-fade-in">
          <div className="glass px-6 py-4 rounded-xl">
            <p className="text-song-meta text-text-main">{toastMessage}</p>
          </div>
        </div>
      )}
    </main>
  );
}
