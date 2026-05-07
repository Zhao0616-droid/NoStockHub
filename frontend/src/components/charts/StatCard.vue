<template>
  <div class="stat-card" :style="cardStyle">
    <div class="stat-icon" v-if="icon || $slots.icon">
      <slot name="icon">
        <el-icon :size="22" :color="color">
          <component :is="icon" />
        </el-icon>
      </slot>
    </div>
    <div class="stat-body">
      <span class="stat-value" ref="valueRef">{{ displayValue }}</span>
      <span class="stat-label">{{ label }}</span>
      <span class="stat-trend" v-if="trend !== undefined" :class="trendClass">
        <el-icon :size="12">
          <CaretTop v-if="trend > 0" />
          <CaretBottom v-else-if="trend < 0" />
          <Minus v-else />
        </el-icon>
        {{ Math.abs(trend) }}%
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { CaretTop, CaretBottom, Minus } from '@element-plus/icons-vue'

const props = defineProps({
  value: { type: [Number, String], default: 0 },
  label: { type: String, default: '' },
  icon: { type: [Object, String], default: null },
  color: { type: String, default: '#409EFF' },
  trend: { type: Number, default: undefined },
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  decimals: { type: Number, default: 0 },
  animated: { type: Boolean, default: true },
  duration: { type: Number, default: 800 }
})

const displayValue = ref('0')
const valueRef = ref(null)

const cardStyle = {
  '--stat-color': props.color
}

const trendClass = computed(() => ({
  'trend-up': props.trend > 0,
  'trend-down': props.trend < 0,
  'trend-flat': props.trend === 0
}))

function animateValue() {
  if (!props.animated) {
    displayValue.value = formatValue(props.value)
    return
  }

  const target = Number(props.value) || 0
  const start = 0
  const startTime = performance.now()

  function step(currentTime) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / props.duration, 1)
    // easeOutCubic
    const eased = 1 - Math.pow(1 - progress, 3)
    const current = start + (target - start) * eased
    displayValue.value = formatValue(current)
    if (progress < 1) {
      requestAnimationFrame(step)
    }
  }

  requestAnimationFrame(step)
}

function formatValue(v) {
  const num = Number(v)
  if (isNaN(num)) return String(v)
  const fixed = num.toFixed(props.decimals)
  return `${props.prefix}${fixed}${props.suffix}`
}

onMounted(animateValue)

watch(() => props.value, () => {
  animateValue()
})
</script>

<style scoped lang="scss">
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s, transform 0.2s;
  border-left: 3px solid var(--stat-color);

  &:hover {
    box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    transform: translateY(-1px);
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--stat-color) 12%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-trend {
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 2px;

  &.trend-up { color: #67C23A; }
  &.trend-down { color: #F56C6C; }
  &.trend-flat { color: #909399; }
}
</style>
