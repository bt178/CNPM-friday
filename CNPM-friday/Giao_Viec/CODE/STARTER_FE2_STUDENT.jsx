// FE2 - Student Dashboard & Team Management
// Paste into src/pages/StudentDashboard.jsx

import React, { useState, useEffect } from 'react';
import { Table, Button, Form, Modal, Card, Row, Col, message, Space, Tag, Input } from 'antd';
import { PlusOutlined, LoginOutlined } from '@ant-design/icons';
import api from '../services/api';

export default function StudentDashboard() {
    const [topics, setTopics] = useState([]);
    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(false);
    const [createTeamModalVisible, setCreateTeamModalVisible] = useState(false);
    const [joinTeamModalVisible, setJoinTeamModalVisible] = useState(false);
    const [createForm] = Form.useForm();
    const [joinForm] = Form.useForm();

    useEffect(() => {
        fetchTopics();
        fetchTeams();
    }, []);

    const fetchTopics = async () => {
        try {
            const response = await api.get('/topics');
            // Filter only APPROVED topics
            const approvedTopics = response.data.filter(t => t.status === 'APPROVED');
            setTopics(approvedTopics);
        } catch (error) {
            message.error('Failed to load topics');
        }
    };

    const fetchTeams = async () => {
        setLoading(true);
        try {
            const response = await api.get('/teams');
            setTeams(response.data);
        } catch (error) {
            message.error('Failed to load teams');
        }
        setLoading(false);
    };

    const handleCreateTeam = async (values) => {
        try {
            const response = await api.post('/teams', {
                name: values.teamName,
                project_id: values.projectId,
                description: values.description || '',
            });
            message.success(`Team created! Join code: ${response.data.join_code}`);
            setCreateTeamModalVisible(false);
            createForm.resetFields();
            fetchTeams();
        } catch (error) {
            message.error(error.response?.data?.detail || 'Failed to create team');
        }
    };

    const handleJoinTeam = async (values) => {
        try {
            const response = await api.post('/teams/join', {
                join_code: values.joinCode,
            });
            message.success(`Successfully joined ${response.data.name}`);
            setJoinTeamModalVisible(false);
            joinForm.resetFields();
            fetchTeams();
        } catch (error) {
            message.error(error.response?.data?.detail || 'Failed to join team');
        }
    };

    const topicsColumns = [
        { title: 'Title', dataIndex: 'title', key: 'title' },
        { title: 'Description', dataIndex: 'description', key: 'description', width: 300 },
        { title: 'Status', dataIndex: 'status', key: 'status', render: (status) => <Tag color="green">{status}</Tag> },
    ];

    const teamsColumns = [
        { title: 'Team Name', dataIndex: 'name', key: 'name' },
        { title: 'Members', dataIndex: 'member_count', key: 'member_count' },
        {
            title: 'Status',
            dataIndex: 'is_finalized',
            key: 'status',
            render: (isFinalized) => <Tag color={isFinalized ? 'red' : 'blue'}>{isFinalized ? 'Finalized' : 'Active'}</Tag>,
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button type="link" href={`/student/teams/${record.team_id}`}>
                        View Details
                    </Button>
                </Space>
            ),
        },
    ];

    return (
        <div style={{ padding: '24px' }}>
            <h1>Student Dashboard</h1>

            <Row gutter={16} style={{ marginBottom: '32px' }}>
                <Col span={12}>
                    <Card>
                        <h2>My Teams</h2>
                        <Space>
                            <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                onClick={() => setCreateTeamModalVisible(true)}
                            >
                                Create Team
                            </Button>
                            <Button
                                icon={<LoginOutlined />}
                                onClick={() => setJoinTeamModalVisible(true)}
                            >
                                Join Team
                            </Button>
                        </Space>
                    </Card>
                </Col>
            </Row>

            <h2>Available Topics</h2>
            <Table
                columns={topicsColumns}
                dataSource={topics.map(t => ({ ...t, key: t.topic_id }))}
                pagination={{ pageSize: 5 }}
                style={{ marginBottom: '32px' }}
            />

            <h2>Your Teams</h2>
            <Table
                columns={teamsColumns}
                dataSource={teams.map(t => ({ ...t, key: t.team_id }))}
                loading={loading}
                pagination={{ pageSize: 10 }}
            />

            {/* Create Team Modal */}
            <Modal
                title="Create New Team"
                visible={createTeamModalVisible}
                onOk={() => createForm.submit()}
                onCancel={() => setCreateTeamModalVisible(false)}
            >
                <Form
                    form={createForm}
                    layout="vertical"
                    onFinish={handleCreateTeam}
                >
                    <Form.Item
                        label="Team Name"
                        name="teamName"
                        rules={[{ required: true }]}
                    >
                        <Input placeholder="Enter team name" />
                    </Form.Item>
                    <Form.Item
                        label="Project ID"
                        name="projectId"
                        rules={[{ required: true }]}
                    >
                        <Input type="number" placeholder="Project ID" />
                    </Form.Item>
                    <Form.Item label="Description" name="description">
                        <textarea placeholder="Team description" rows={3} />
                    </Form.Item>
                </Form>
            </Modal>

            {/* Join Team Modal */}
            <Modal
                title="Join Team"
                visible={joinTeamModalVisible}
                onOk={() => joinForm.submit()}
                onCancel={() => setJoinTeamModalVisible(false)}
            >
                <Form
                    form={joinForm}
                    layout="vertical"
                    onFinish={handleJoinTeam}
                >
                    <Form.Item
                        label="Join Code"
                        name="joinCode"
                        rules={[{ required: true }]}
                    >
                        <Input placeholder="Enter 6-digit join code" />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
}
