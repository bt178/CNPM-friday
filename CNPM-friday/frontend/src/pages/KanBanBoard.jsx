import React, { useState, useEffect } from 'react';
import { Layout, Typography, Button, Card, Col, Row, Select, Modal, Form, Input, message, Tag } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { taskService } from '../services/api';
import MainLayout from '../components/MainLayout';

const { Title } = Typography;
const { Content } = Layout;
const { Option } = Select;

const KanBanBoard = () => {
    const [sprints, setSprints] = useState([]);
    const [currentSprintId, setCurrentSprintId] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);

    // Modal controls
    const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
    const [isSprintModalOpen, setIsSprintModalOpen] = useState(false);
    const [taskForm] = Form.useForm();
    const [sprintForm] = Form.useForm();

    const fetchSprints = async () => {
        try {
            // Assuming there's an endpoint to get all sprints, otherwise we might need to adjust
            // The user request mentioned POST /api/v1/tasks/sprints and GET /api/v1/tasks/sprints/{sprint_id}
            // but not "Get All Sprints". I'll assume we can get them or there's a default.
            // For now, I'll simulate or try to fetch tasks directly if no sprints.
            // Or maybe GET /api/v1/tasks returns all tasks?
            // Let's assume we can fetch tasks without sprint first, or sprints are needed.
            // I'll try to fetch tasks globally if no sprint API for "list".
            const res = await taskService.getAllTasks();
            const allTasks = res.data || [];
            setTasks(allTasks);

            // If tasks have sprint info, extracting sprints (simplified)
            // Ideally we have an API to list sprints.
        } catch (error) {
            console.error("Failed to fetch initial data", error);
        }
    };

    const fetchSprintTasks = async (sprintId) => {
        setLoading(true);
        try {
            const res = await taskService.getSprintTasks(sprintId);
            setTasks(res.data || []);
        } catch (error) {
            console.error("Failed to fetch sprint tasks", error);
            message.error("Failed to load tasks");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Initial load
        fetchSprints();
    }, []);

    useEffect(() => {
        if (currentSprintId) {
            fetchSprintTasks(currentSprintId);
        } else {
            // Maybe fetch all if no sprint selected
            // fetchSprints loaded all tasks initially
        }
    }, [currentSprintId]);

    const handleCreateTask = async (values) => {
        try {
            await taskService.createTask({ ...values, sprint_id: currentSprintId });
            message.success('Task created');
            setIsTaskModalOpen(false);
            taskForm.resetFields();
            if (currentSprintId) fetchSprintTasks(currentSprintId);
            else fetchSprints();
        } catch (error) {
            message.error('Failed to create task');
        }
    };

    const handleCreateSprint = async (values) => {
        try {
            const res = await taskService.createSprint(values);
            message.success('Sprint created');
            setIsSprintModalOpen(false);
            sprintForm.resetFields();
            // setSprints logic would go here if we had list API
            // For now just select it if returned
            if (res.data && res.data.id) setCurrentSprintId(res.data.id);
        } catch (error) {
            message.error('Failed to create sprint');
        }
    };

    const handleStatusChange = async (taskId, newStatus) => {
        try {
            await taskService.changeStatus(taskId, newStatus);
            message.success("Status updated");
            // Optimistic update
            setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
        } catch (error) {
            message.error("Failed to update status");
        }
    };

    const columns = ['To Do', 'In Progress', 'Done'];

    return (
        <MainLayout>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
                <Title level={2}>Kanban Board</Title>
                <div style={{ display: 'flex', gap: 10 }}>
                    <Button onClick={() => setIsSprintModalOpen(true)}>New Sprint</Button>
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsTaskModalOpen(true)}>
                        New Task
                    </Button>
                </div>
            </div>

            {/* Sprints controls if needed */}
            <div style={{ marginBottom: 16 }}>
                <Select
                    style={{ width: 200 }}
                    placeholder="Select Sprint"
                    onChange={setCurrentSprintId}
                    value={currentSprintId}
                    allowClear
                >
                    {/* Populate if we had sprints list */}
                    {sprints.map(s => <Option key={s.id} value={s.id}>{s.name}</Option>)}
                </Select>
            </div>

            <Row gutter={16}>
                {columns.map(status => (
                    <Col span={8} key={status}>
                        <Card title={status} style={{ background: '#f0f2f5', minHeight: 500 }}>
                            {tasks.filter(t => (t.status || 'To Do') === status).map(task => (
                                <Card
                                    key={task.id}
                                    style={{ marginBottom: 10, cursor: 'move' }}
                                    size="small"
                                    title={task.title}
                                    extra={<Tag>{task.priority || 'Normal'}</Tag>}
                                >
                                    <p>{task.description}</p>
                                    <Select
                                        defaultValue={task.status}
                                        size="small"
                                        onChange={(val) => handleStatusChange(task.id, val)}
                                        style={{ width: '100%' }}
                                    >
                                        {columns.map(c => <Option key={c} value={c}>{c}</Option>)}
                                    </Select>
                                </Card>
                            ))}
                        </Card>
                    </Col>
                ))}
            </Row>

            {/* Create Task Modal */}
            <Modal title="Create Task" open={isTaskModalOpen} onCancel={() => setIsTaskModalOpen(false)} onOk={() => taskForm.submit()}>
                <Form form={taskForm} layout="vertical" onFinish={handleCreateTask}>
                    <Form.Item name="title" label="Title" rules={[{ required: true }]}><Input /></Form.Item>
                    <Form.Item name="description" label="Description"><Input.TextArea /></Form.Item>
                    <Form.Item name="status" label="Status" initialValue="To Do">
                        <Select>
                            {columns.map(c => <Option key={c} value={c}>{c}</Option>)}
                        </Select>
                    </Form.Item>
                </Form>
            </Modal>

            {/* Create Sprint Modal */}
            <Modal title="Create Sprint" open={isSprintModalOpen} onCancel={() => setIsSprintModalOpen(false)} onOk={() => sprintForm.submit()}>
                <Form form={sprintForm} layout="vertical" onFinish={handleCreateSprint}>
                    <Form.Item name="name" label="Sprint Name" rules={[{ required: true }]}><Input /></Form.Item>
                    <Form.Item name="goal" label="Sprint Goal"><Input.TextArea /></Form.Item>
                </Form>
            </Modal>
        </MainLayout>
    );
};

export default KanBanBoard;
