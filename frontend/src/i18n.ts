export function tError(status?: number, serverDetail?: string): string {
  const map: Record<number, string> = {
    409: "このセッション内には同じ名前のデータセットが既に存在します",
    404: "データセットが見つかりません",
    400: "不正な入力です",
  };
  return map[status ?? -1] ?? serverDetail ?? "エラーが発生しました";
}

