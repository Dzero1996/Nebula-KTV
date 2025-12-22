"use client";

/**
 * SearchBar 组件 - 全局搜索框
 * 车载优化：高度 > 60px，防抖搜索 300ms
 * Requirements: 3.1, 3.2
 */

import * as React from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface SearchBarProps {
  /** 搜索回调，防抖后触发 */
  onSearch: (query: string) => void;
  /** 占位符文本 */
  placeholder?: string;
  /** 初始值 */
  defaultValue?: string;
  /** 自定义类名 */
  className?: string;
  /** 是否正在加载 */
  loading?: boolean;
}

export function SearchBar({
  onSearch,
  placeholder = "搜索歌曲或歌手...",
  defaultValue = "",
  className,
  loading = false,
}: SearchBarProps) {
  const [value, setValue] = React.useState(defaultValue);
  const debounceRef = React.useRef<NodeJS.Timeout | null>(null);

  // 防抖搜索 - 300ms
  const handleChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      setValue(newValue);

      // 清除之前的定时器
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      // 设置新的防抖定时器
      debounceRef.current = setTimeout(() => {
        onSearch(newValue);
      }, 300);
    },
    [onSearch]
  );

  // 清除搜索
  const handleClear = React.useCallback(() => {
    setValue("");
    onSearch("");
    // 清除待执行的防抖
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
  }, [onSearch]);

  // 组件卸载时清除定时器
  React.useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  return (
    <div className={cn("relative w-full", className)}>
      {/* 搜索图标 */}
      <Search
        className={cn(
          "absolute left-4 top-1/2 -translate-y-1/2 h-6 w-6 text-text-muted",
          loading && "animate-pulse"
        )}
      />

      {/* 输入框 - 高度 > 60px 满足车载触控要求 */}
      <Input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className={cn(
          "h-16 pl-14 pr-14 text-xl",
          "bg-surface border-border rounded-xl",
          "text-text-main placeholder:text-text-muted",
          "focus-visible:ring-2 focus-visible:ring-primary focus-visible:border-primary",
          "transition-all duration-200"
        )}
      />

      {/* 清除按钮 - 仅在有内容时显示 */}
      {value && (
        <button
          type="button"
          onClick={handleClear}
          className={cn(
            "absolute right-4 top-1/2 -translate-y-1/2",
            "h-10 w-10 flex items-center justify-center",
            "rounded-full bg-muted/50 hover:bg-muted",
            "text-text-muted hover:text-text-main",
            "transition-colors duration-150",
            "press-effect"
          )}
          aria-label="清除搜索"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  );
}
