<template>
  <div class="chart-demo">
    <h2>📊 图表组件库 Demo</h2>
    <p class="subtitle">components/charts/ 全部组件效果预览</p>

    <!-- StatCard 统计卡片 -->
    <section>
      <h3>StatCard · 统计卡片</h3>
      <div class="stat-row">
        <StatCard :value="12" label="进行中项目" color="#409EFF" :icon="Folder" :trend="8" />
        <StatCard :value="85" label="任务完成率" color="#67C23A" suffix="%" :trend="5" />
        <StatCard :value="3" label="活跃冲刺" color="#E6A23C" :icon="Timer" :trend="-2" />
        <StatCard :value="128" label="总工时" color="#F56C6C" suffix="h" :trend="0" />
      </div>
    </section>

    <!-- ProgressRing 进度环形图 -->
    <section>
      <h3>ProgressRing · 进度环形图</h3>
      <div class="ring-row">
        <div class="ring-item">
          <ProgressRing :percent="65" color="#409EFF" label="项目进度" />
          <span class="ring-caption">默认样式</span>
        </div>
        <div class="ring-item">
          <ProgressRing :percent="100" color="#67C23A" label="已完成" sublabel="8/8 任务" />
          <span class="ring-caption">完成态</span>
        </div>
        <div class="ring-item">
          <ProgressRing :percent="22" color="#E6A23C" label="进行中" :line-width="8" size="140px" />
          <span class="ring-caption">小尺寸 + 细线条</span>
        </div>
        <div class="ring-item">
          <ProgressRing :percent="0" color="#909399" label="未开始" />
          <span class="ring-caption">0% 状态</span>
        </div>
      </div>
    </section>

    <!-- BurndownChart 燃尽图 -->
    <section>
      <h3>BurndownChart · 冲刺燃尽图</h3>
      <BurndownChart
        :dates="burndownDates"
        :ideal="burndownIdeal"
        :actual="burndownActual"
        height="350px"
      />
    </section>

    <!-- TaskDistribution 任务分布图 -->
    <section>
      <h3>TaskDistribution · 任务分布图</h3>
      <div class="dist-row">
        <div class="dist-item">
          <h4>饼图 — 按状态</h4>
          <TaskDistribution :data="statusData" type="pie" height="300px" />
        </div>
        <div class="dist-item">
          <h4>饼图 — 按优先级</h4>
          <TaskDistribution :data="priorityData" type="pie" height="300px" />
        </div>
        <div class="dist-item">
          <h4>柱状图 — 按负责人</h4>
          <TaskDistribution :data="assigneeData" type="bar" height="300px" />
        </div>
        <div class="dist-item">
          <h4>柱状图 — 按类型</h4>
          <TaskDistribution :data="typeData" type="bar" height="300px" />
        </div>
      </div>
    </section>

    <!-- TrendChart 趋势折线图 -->
    <section>
      <h3>TrendChart · 趋势折线图</h3>
      <div class="trend-row">
        <div class="trend-item">
          <h4>折线 — 每日完成任务</h4>
          <TrendChart
            :x-data="trendDates"
            :series="[{ name: '完成任务', data: [2,5,3,8,6,4,9,7,5,10,8,6,11,9], color: '#67C23A' }]"
            :smooth="true"
            height="280px"
          />
        </div>
        <div class="trend-item">
          <h4>面积图 — 多系列对比</h4>
          <TrendChart
            :x-data="trendDates"
            :series="[
              { name: '新增任务', data: [3,4,5,2,6,3,7,4,5,3,6,4,8,5], color: '#F56C6C' },
              { name: '完成任务', data: [2,3,4,5,3,4,6,5,4,7,5,6,7,4], color: '#67C23A' }
            ]"
            :show-area="true"
            height="280px"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import {
  StatCard, ProgressRing, BurndownChart,
  TaskDistribution, TrendChart
} from '@/components/charts'
import { Folder, Timer } from '@element-plus/icons-vue'

// ---------- 燃尽图数据 ----------
const burndownDates = ['5/1','5/2','5/3','5/4','5/5','5/6','5/7','5/8','5/9','5/10','5/11','5/12','5/13','5/14']
const burndownIdeal = [20,18,17,15,14,12,11,9,7,6,4,3,1,0]
const burndownActual = [20,19,18,16,15,14,12,10,9,8,6,5,3,null]

// ---------- 分布图数据 ----------
const statusData = [
  { name: '待办', value: 8, color: '#909399' },
  { name: '进行中', value: 5, color: '#409EFF' },
  { name: '审核中', value: 3, color: '#E6A23C' },
  { name: '已完成', value: 12, color: '#67C23A' },
  { name: '阻塞', value: 2, color: '#F56C6C' }
]

const priorityData = [
  { name: '低', value: 6, color: '#909399' },
  { name: '中', value: 10, color: '#409EFF' },
  { name: '高', value: 8, color: '#E6A23C' },
  { name: '紧急', value: 4, color: '#F56C6C' }
]

const assigneeData = [
  { name: '张三', value: 12, color: '#409EFF' },
  { name: '李四', value: 8, color: '#67C23A' },
  { name: '王五', value: 6, color: '#E6A23C' }
]

const typeData = [
  { name: '任务', value: 18, color: '#409EFF' },
  { name: '缺陷', value: 5, color: '#F56C6C' },
  { name: '史诗', value: 3, color: '#E6A23C' }
]

// ---------- 趋势图数据 ----------
const trendDates = ['5/1','5/2','5/3','5/4','5/5','5/6','5/7','5/8','5/9','5/10','5/11','5/12','5/13','5/14']
</script>

<style scoped lang="scss">
.chart-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;

  h2 { margin: 0 0 4px 0; font-size: 24px; }
  .subtitle { color: #909399; margin: 0 0 32px 0; font-size: 14px; }
}

section {
  margin-bottom: 40px;

  h3 {
    margin: 0 0 16px 0;
    font-size: 17px;
    color: var(--el-text-color-primary);
    padding-bottom: 8px;
    border-bottom: 1px solid #ebeef5;
  }
}

// Stat 行
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

// Ring 行
.ring-row {
  display: flex;
  gap: 32px;
  align-items: flex-start;

  .ring-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .ring-caption {
    font-size: 12px;
    color: #909399;
  }
}

// 分布图行
.dist-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;

  .dist-item {
    background: #fff;
    border-radius: 8px;
    border: 1px solid #ebeef5;
    padding: 16px;

    h4 {
      margin: 0 0 8px 0;
      font-size: 14px;
      color: var(--el-text-color-regular);
    }
  }
}

// 趋势图行
.trend-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;

  .trend-item {
    background: #fff;
    border-radius: 8px;
    border: 1px solid #ebeef5;
    padding: 16px;

    h4 {
      margin: 0 0 8px 0;
      font-size: 14px;
      color: var(--el-text-color-regular);
    }
  }
}

@media (max-width: 900px) {
  .stat-row { grid-template-columns: repeat(2, 1fr); }
  .dist-row, .trend-row { grid-template-columns: 1fr; }
  .ring-row { flex-wrap: wrap; }
}
</style>
