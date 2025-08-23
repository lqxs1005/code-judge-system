<template>
  <a-layout style="background: #fff; min-height: 100vh;">
    <a-page-header
      title="题目管理"
      sub-title="管理和创建编程题"
      style="border-bottom: 1px solid #f0f0f0;"
    >
      <template #extra>
        <a-button type="primary" @click="showCreateModal = true" icon>
          <template #icon><PlusOutlined /></template>
          新建题目
        </a-button>
        <a-button style="margin-left: 8px" @click="showAIModal = true" icon>
          <template #icon><RobotOutlined /></template>
          AI生成
        </a-button>
      </template>
    </a-page-header>

    <div style="padding: 24px;">
      <a-form layout="inline" @submit.prevent>
        <a-form-item>
          <a-input
            v-model:value="searchTitle"
            placeholder="按标题搜索"
            allow-clear
            @pressEnter="onSearch"
            style="width: 200px"
          />
        </a-form-item>
        <a-form-item>
          <a-select
            v-model:value="searchType"
            placeholder="题型"
            allow-clear
            style="width: 120px"
            @change="onSearch"
          >
            <a-select-option value="choice">选择题</a-select-option>
            <a-select-option value="fill_blank">填空题</a-select-option>
            <a-select-option value="short_answer">简答题</a-select-option>
            <a-select-option value="coding">编程题</a-select-option>
            <a-select-option value="code_snippet">代码补全</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-select
            v-model:value="searchDifficulty"
            placeholder="难度"
            allow-clear
            style="width: 120px"
            @change="onSearch"
          >
            <a-select-option value="1">简单</a-select-option>
            <a-select-option value="2">普通</a-select-option>
            <a-select-option value="3">中等</a-select-option>
            <a-select-option value="4">较难</a-select-option>
            <a-select-option value="5">困难</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="onSearch" icon>
            <template #icon><SearchOutlined /></template>
            查询
          </a-button>
        </a-form-item>
      </a-form>

      <a-table
        :columns="columns"
        :data-source="problemStore.list"
        :loading="problemStore.loading"
        :pagination="pagination"
        row-key="id"
        style="margin-top: 16px"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'difficulty'">
            <a-tag :color="difficultyColor(record.difficulty)">
              {{ difficultyText(record.difficulty) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'type'">
            {{ typeText(record.type) }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" @click="onEdit(record)">
                <EditOutlined /> 编辑
              </a-button>
              <a-popconfirm
                title="确定要删除该题目吗？"
                ok-text="删除"
                cancel-text="取消"
                @confirm="onDelete(record)"
              >
                <a-button type="link" danger>
                  <DeleteOutlined /> 删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 新建题目模态框 -->
    <a-modal
      v-model:open="showCreateModal"
      title="新建题目"
      :confirm-loading="createLoading"
      @ok="handleCreate"
      @cancel="resetCreateForm"
      destroy-on-close
    >
      <a-form :model="createForm" layout="vertical">
        <a-form-item label="标题" required>
          <a-input v-model:value="createForm.title" />
        </a-form-item>
        <a-form-item label="描述" required>
          <a-textarea v-model:value="createForm.description" rows="3" />
        </a-form-item>
        <a-form-item label="题型" required>
          <a-select v-model:value="createForm.type">
            <a-select-option value="choice">选择题</a-select-option>
            <a-select-option value="fill_blank">填空题</a-select-option>
            <a-select-option value="short_answer">简答题</a-select-option>
            <a-select-option value="coding">编程题</a-select-option>
            <a-select-option value="code_snippet">代码补全</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="难度" required>
          <a-select v-model:value="createForm.difficulty">
            <a-select-option value="1">简单</a-select-option>
            <a-select-option value="2">普通</a-select-option>
            <a-select-option value="3">中等</a-select-option>
            <a-select-option value="4">较难</a-select-option>
            <a-select-option value="5">困难</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- AI生成题目模态框 -->
    <a-modal
      v-model:open="showAIModal"
      title="AI生成题目"
      :confirm-loading="aiLoading"
      @ok="handleAIGenerate"
      @cancel="resetAIForm"
      destroy-on-close
      width="600px"
    >
      <a-form :model="aiForm" layout="vertical">
        <a-form-item label="主题" required>
          <a-input v-model:value="aiForm.topic" />
        </a-form-item>
        <a-form-item label="题型" required>
          <a-select v-model:value="aiForm.type">
            <a-select-option value="choice">选择题</a-select-option>
            <a-select-option value="fill_blank">填空题</a-select-option>
            <a-select-option value="short_answer">简答题</a-select-option>
            <a-select-option value="coding">编程题</a-select-option>
            <a-select-option value="code_snippet">代码补全</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="难度" required>
          <a-select v-model:value="aiForm.difficulty">
            <a-select-option value="1">简单</a-select-option>
            <a-select-option value="2">普通</a-select-option>
            <a-select-option value="3">中等</a-select-option>
            <a-select-option value="4">较难</a-select-option>
            <a-select-option value="5">困难</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item v-if="aiForm.type === 'coding'" label="编程语言" required>
          <a-select v-model:value="aiForm.language">
            <a-select-option value="python">Python</a-select-option>
            <a-select-option value="c">C</a-select-option>
            <a-select-option value="cpp">C++</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button @click="resetAIForm">取消</a-button>
        <a-button type="primary" :loading="aiLoading" @click="handleAIGenerate">生成</a-button>
      </template>
      <div v-if="aiPreview" style="margin-top: 16px;">
        <a-alert
          message="AI生成题目预览"
          type="info"
          show-icon
          style="margin-bottom: 8px;"
        />
        <pre style="background: #f6f6f6; padding: 12px; border-radius: 4px; max-height: 300px; overflow: auto;">
{{ JSON.stringify(aiPreview, null, 2) }}
        </pre>
        <a-button type="primary" @click="handleAISave" :loading="aiSaveLoading" style="margin-top: 8px;">
          保存为题目
        </a-button>
      </div>
    </a-modal>
  </a-layout>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { useProblemStore } from '@/stores/problemStore'
import http from '@/api/http'
import { message, Modal } from 'ant-design-vue'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  RobotOutlined,
  SearchOutlined
} from '@ant-design/icons-vue'

const problemStore = useProblemStore()

const searchTitle = ref('')
const searchType = ref('')
const searchDifficulty = ref('')

const showCreateModal = ref(false)
const createForm = ref({
  title: '',
  description: '',
  type: '',
  difficulty: ''
})
const createLoading = ref(false)

const showAIModal = ref(false)
const aiForm = ref({
  topic: '',
  type: '',
  difficulty: '',
  language: ''
})
const aiLoading = ref(false)
const aiPreview = ref<any>(null)
const aiSaveLoading = ref(false)

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '标题', dataIndex: 'title', key: 'title' },
  { title: '题型', dataIndex: 'type', key: 'type', width: 100 },
  { title: '难度', dataIndex: 'difficulty', key: 'difficulty', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'actions', width: 160 }
]

const pagination = {
  current: problemStore.page,
  pageSize: problemStore.pageSize,
  total: problemStore.total,
  showTotal: (total: number) => `共 ${total} 条`,
  showQuickJumper: true,
  showSizeChanger: true,
  onChange: (page: number, pageSize: number) => {
    problemStore.page = page
    problemStore.pageSize = pageSize
    problemStore.fetchProblems()
  }
}

function onSearch() {
  problemStore.setQuery({
    title: searchTitle.value,
    type: searchType.value,
    difficulty: searchDifficulty.value
  })
  problemStore.fetchProblems()
}

function difficultyText(val: string | number) {
  const map: any = { 1: '简单', 2: '普通', 3: '中等', 4: '较难', 5: '困难' }
  return map[val] || val
}
function difficultyColor(val: string | number) {
  const map: any = { 1: 'green', 2: 'blue', 3: 'orange', 4: 'red', 5: 'volcano' }
  return map[val] || 'default'
}
function typeText(val: string) {
  const map: any = {
    choice: '选择题',
    fill_blank: '填空题',
    short_answer: '简答题',
    coding: '编程题',
    code_snippet: '代码补全'
  }
  return map[val] || val
}

function resetCreateForm() {
  showCreateModal.value = false
  createForm.value = { title: '', description: '', type: '', difficulty: '' }
}

async function handleCreate() {
  createLoading.value = true
  try {
    await http.post('/problems', createForm.value)
    message.success('题目创建成功')
    resetCreateForm()
    problemStore.fetchProblems()
  } catch (e: any) {
    Modal.error({ title: '创建失败', content: e?.response?.data?.msg || '未知错误' })
  } finally {
    createLoading.value = false
  }
}

function resetAIForm() {
  showAIModal.value = false
  aiForm.value = { topic: '', type: '', difficulty: '', language: '' }
  aiPreview.value = null
}

async function handleAIGenerate() {
  aiLoading.value = true
  aiPreview.value = null
  try {
    const res = await http.post('/ai/generate-problem', aiForm.value)
    aiPreview.value = res.data.problem
    message.success('AI生成成功，请确认后保存')
  } catch (e: any) {
    Modal.error({ title: 'AI生成失败', content: e?.response?.data?.msg || '未知错误' })
  } finally {
    aiLoading.value = false
  }
}

async function handleAISave() {
  if (!aiPreview.value) return
  aiSaveLoading.value = true
  try {
    await http.post('/problems', aiPreview.value)
    message.success('AI题目保存成功')
    resetAIForm()
    problemStore.fetchProblems()
  } catch (e: any) {
    Modal.error({ title: '保存失败', content: e?.response?.data?.msg || '未知错误' })
  } finally {
    aiSaveLoading.value = false
  }
}

function onEdit(record: any) {
  Modal.info({ title: '编辑功能待实现', content: `题目ID: ${record.id}` })
}

async function onDelete(record: any) {
  try {
    await http.delete(`/problems/${record.id}`)
    message.success('删除成功')
    problemStore.fetchProblems()
  } catch (e: any) {
    Modal.error({ title: '删除失败', content: e?.response?.data?.msg || '未知错误' })
  }
}

onMounted(() => {
  problemStore.fetchProblems()
})

watch(
  () => [problemStore.page, problemStore.pageSize],
  () => {
    problemStore.fetchProblems()
  }
)
</script>
