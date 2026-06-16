<template>
  <div class="thankyou-page">
    <div class="card thankyou-card text-center">
      <p style="font-size:56px;margin-bottom:16px">✅</p>
      <h2>提交成功</h2>
      <p class="text-secondary mt-sm">感谢您的参与！</p>
      <router-link to="/" class="btn btn-primary mt-lg">返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.thankyou-page {
  min-height: calc(100vh - var(--header-height));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}
.thankyou-card {
  padding: var(--spacing-2xl) var(--spacing-xl);
  max-width: 400px;
  width: 100%;
}
</style>
