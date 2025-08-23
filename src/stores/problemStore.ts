import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Problem } from '@/types/problem'
import http from '@/api/http'

export const useProblemStore = defineStore('problem', () => {
  const list = ref<Problem[]>([])
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)
  const query = ref({
    title: '',
    type: '',
    difficulty: ''
  })

  async function fetchProblems() {
    loading.value = true
    try {
      const params: any = {
        page: page.value,
        page_size: pageSize.value,
        ...query.value
      }
      // 清理空参数
      Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
      const res = await http.get('/problems', { params })
      list.value = res.data.items || res.data.data || []
      total.value = res.data.total || 0
    } catch (e) {
      list.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  function setQuery(newQuery: Partial<typeof query.value>) {
    query.value = { ...query.value, ...newQuery }
    page.value = 1
  }

  return {
    list,
    loading,
    total,
    page,
    pageSize,
    query,
    fetchProblems,
    setQuery
  }
})
