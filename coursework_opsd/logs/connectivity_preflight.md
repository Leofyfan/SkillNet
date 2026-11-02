# 连通性检查

在正式 SDK 检索前，用 Python urllib 诊断公开服务连通性（不检查或选用候选内容）：

- `http://api-skillnet.openkg.cn/v1/search?q=paper&limit=1`：HTTP 200，返回 `success: true`，终端仅显示前 180 字节。此诊断也是一次检索端点请求，计入总 API 请求数；完整正文未保存，不能当作正式候选证据。
- 相同路径的 HTTPS 请求：证书主机名不匹配，`CERTIFICATE_VERIFY_FAILED`。未关闭 TLS 验证；后续使用 SDK 仓库默认的公开 HTTP 端点，不传入任何凭据。

正式候选与选择以 SDK 脚本保存的 JSON 为准。以上为操作后补记，未取得单独耗时。
