#!/usr/bin/env node
// 静态检查：单文件 HTML 是否可离线、有无占位符残留、页数是否正常
import fs from "node:fs";

const file = process.argv[2];
if (!file) {
  console.error("用法: node check.mjs out/index.html");
  process.exit(1);
}
const html = fs.readFileSync(file, "utf8");
// 去掉 base64 内联资源，避免把图片字节中的 NaN/undefined 误判为文本缺陷
const visible = html.replace(/data:[^"')]+/g, "data:…");
const problems = [];

if (/<script[^>]+src=/i.test(html) || /<link[^>]+href=/i.test(html)) problems.push("存在外链脚本或样式，离线不可用");
if (/https?:\/\//i.test(visible.replace(/<!DOCTYPE[^>]*>/i, ""))) problems.push("存在 http(s) 外链");
if (/\{\{[^{}]{0,40}\}\}/.test(visible)) problems.push("存在未替换的模板占位符");
if (/\bundefined\b/.test(visible)) problems.push("存在 undefined 文本");
if (/NaN/.test(visible)) problems.push("存在 NaN 数值");
const slides = (html.match(/class="slide /g) || []).length;
if (slides === 0) problems.push("未检测到幻灯片节点");
if (!/<meta charset="utf-8">/i.test(html)) problems.push("缺少 UTF-8 声明");

console.log(`幻灯片 ${slides} 页，文件 ${(html.length / 1024).toFixed(1)} KB`);
if (problems.length) {
  console.log("FAIL:");
  problems.forEach((p) => console.log(" - " + p));
  process.exit(1);
}
console.log("PASS: 无外链、无占位符、结构正常");
