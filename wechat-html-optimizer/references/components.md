# 微信公众号 HTML 组件库

## 1. 标题组件

### 1.1 左边框标题
```html
<p style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #667eea;">
  标题文字
</p>
```

### 1.2 底部线条标题
```html
<p style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #667eea; display: inline-block;">
  标题文字
</p>
```

### 1.3 带背景的标题
```html
<p style="font-size: 18px; font-weight: 600; color: #fff; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;">
  标题文字
</p>
```

### 1.4 序号标题
```html
<p style="font-size: 17px; font-weight: 700; color: #e74c3c; margin-bottom: 12px;">
  ① 第一点标题
</p>
```

---

## 2. 卡片组件

### 2.1 基础白卡片
```html
<div style="background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
  <p style="margin-bottom: 0;">卡片内容</p>
</div>
```

### 2.2 灰底信息卡片
```html
<div style="background: #f8f9fc; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
  <p style="margin-bottom: 0;">卡片内容</p>
</div>
```

### 2.3 渐变强调卡片
```html
<div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
  <p style="color: #fff; font-size: 18px; font-weight: 700; margin-bottom: 14px; text-align: center;">
    卡片标题
  </p>
  <div style="background: rgba(255,255,255,0.95); border-radius: 8px; padding: 16px;">
    <p style="color: #333; margin-bottom: 0;">卡片内容</p>
  </div>
</div>
```

### 2.4 核心观点卡片（居中）
```html
<p style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 16px 20px; border-radius: 8px; font-weight: 600; font-size: 17px; margin-bottom: 24px; text-align: center;">
  核心观点文字
</p>
```

---

## 3. 提示框组件

### 3.1 黄色提示（结论/要点）
```html
<p style="background: #fff3cd; padding: 14px 18px; border-radius: 8px; border-left: 4px solid #ffc107; color: #856404; font-weight: 600; margin-bottom: 20px;">
  💡 结论：这是一个重要的结论
</p>
```

### 3.2 蓝色信息框
```html
<p style="background: #e8f4fd; padding: 12px 16px; border-radius: 6px; color: #1a5276; margin-bottom: 16px; font-size: 15px;">
  📌 提示信息内容
</p>
```

### 3.3 绿色成功框
```html
<p style="background: #d4edda; padding: 12px 16px; border-radius: 6px; color: #155724; margin-bottom: 16px; font-size: 15px;">
  ✅ 正确做法或成功提示
</p>
```

### 3.4 红色警告框
```html
<p style="background: #f8d7da; padding: 12px 16px; border-radius: 6px; color: #721c24; margin-bottom: 16px; font-size: 15px;">
  ⚠️ 警告或错误提示
</p>
```

---

## 4. 标签/徽章组件

### 4.1 实心标签
```html
<span style="background: #667eea; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 14px; font-weight: 600;">标签文字</span>
```

### 4.2 成功标签
```html
<span style="background: #28a745; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 14px; font-weight: 600;">成功</span>
```

### 4.3 警告标签
```html
<span style="background: #ffc107; color: #333; padding: 4px 10px; border-radius: 4px; font-size: 14px; font-weight: 600;">注意</span>
```

### 4.4 标签+说明组合
```html
<p style="margin-bottom: 12px;">
  <span style="background: #667eea; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 14px; font-weight: 600;">关键词</span>
  <span style="color: #555; margin-left: 8px;">= 对应的解释说明文字</span>
</p>
```

---

## 5. 分隔线组件

### 5.1 细线分隔
```html
<hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
```

### 5.2 渐变分隔线
```html
<div style="height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent); margin: 32px 0;"></div>
```

### 5.3 点状分隔
```html
<p style="text-align: center; color: #ccc; font-size: 24px; letter-spacing: 8px; margin: 24px 0;">· · ·</p>
```

---

## 6. 列表组件

### 6.1 要点列表（带图标）
```html
<div style="margin-bottom: 16px;">
  <p style="color: #333; margin-bottom: 10px;">✓ 第一点内容</p>
  <p style="color: #333; margin-bottom: 10px;">✓ 第二点内容</p>
  <p style="color: #333; margin-bottom: 0;">✓ 第三点内容</p>
</div>
```

### 6.2 禁止事项列表
```html
<div style="margin-bottom: 16px;">
  <p style="color: #666; margin-bottom: 8px;">✗ 不要做的事情一</p>
  <p style="color: #666; margin-bottom: 8px;">✗ 不要做的事情二</p>
  <p style="color: #666; margin-bottom: 0;">✗ 不要做的事情三</p>
</div>
```

### 6.3 普通列表
```html
<p style="color: #666; margin-bottom: 0; font-size: 15px;">
  • 第一项<br>
  • 第二项<br>
  • 第三项<br>
  • 第四项
</p>
```

---

## 7. 引用/注释组件

### 7.1 左边框引用
```html
<div style="border-left: 3px solid #ddd; padding-left: 16px; color: #666; font-style: italic; margin: 20px 0;">
  <p style="margin-bottom: 0;">引用的文字内容</p>
</div>
```

### 7.2 底部注释
```html
<p style="font-size: 13px; color: #999; margin-top: 24px; padding-top: 16px; border-top: 1px solid #eee;">
  * 注释或补充说明文字
</p>
```

---

## 8. 总结/结尾组件

### 8.1 深色总结框
```html
<p style="background: #1a1a2e; color: #fff; padding: 18px 20px; border-radius: 8px; font-weight: 600; font-size: 17px; text-align: center; margin-bottom: 0;">
  🔑 总结：核心结论文字
</p>
```

### 8.2 行动号召框
```html
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 24px; text-align: center; margin-top: 32px;">
  <p style="color: #fff; font-size: 18px; font-weight: 700; margin-bottom: 8px;">喜欢这篇文章？</p>
  <p style="color: rgba(255,255,255,0.9); font-size: 15px; margin-bottom: 0;">点赞 + 在看 + 转发，让更多人看到</p>
</div>
```

---

## 9. 完整页面模板

```html
<section style="padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; font-size: 16px;">

  <!-- 开场引言 -->
  <p style="margin-bottom: 20px;">
    开场文字...
  </p>
  
  <!-- 核心观点卡片 -->
  <p style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 16px 20px; border-radius: 8px; font-weight: 600; font-size: 17px; margin-bottom: 24px; text-align: center;">
    核心观点
  </p>

  <!-- 小节标题 -->
  <p style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #667eea;">
    第一部分标题
  </p>
  
  <!-- 正文段落 -->
  <p style="margin-bottom: 16px; color: #555;">
    正文内容...
  </p>

  <!-- 信息卡片 -->
  <div style="background: #f8f9fc; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
    <p style="margin-bottom: 0;">卡片内容</p>
  </div>

  <!-- 提示框 -->
  <p style="background: #fff3cd; padding: 14px 18px; border-radius: 8px; border-left: 4px solid #ffc107; color: #856404; font-weight: 600; margin-bottom: 32px;">
    💡 结论：重要结论
  </p>

  <!-- 总结 -->
  <p style="background: #1a1a2e; color: #fff; padding: 18px 20px; border-radius: 8px; font-weight: 600; font-size: 17px; text-align: center; margin-bottom: 0;">
    🔑 最终总结
  </p>

</section>
<p style="display: none;">
  <mp-style-type data-value="10000"></mp-style-type>
</p>
```
