import React, { useState, useEffect } from 'react';
import { Layout, Typography, Button, Table, Modal, Form, Input, message, Row, Col, Card } from 'antd';
import { PlusOutlined, TeamOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { teamService } from '../services/api';
import MainLayout from '../components/MainLayout';

const { Title, Text } = Typography;
const { Content } = Layout;

const TeamManagement = () => {
    const navigate = useNavigate();
    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
    const [joinForm] = Form.useForm();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [form] = Form.useForm();

    const fetchTeams = async () => {
        setLoading(true);
        try {
            const res = await teamService.getAll();
            setTeams(res.data || []);
        } catch (error) {
            console.error("Failed to fetch teams", error);
            message.error("Failed to load teams");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTeams();
    }, []);

    const handleCreateTeam = async (values) => {
        try {
            await teamService.create(values);
            message.success('Team created successfully');
            setIsModalOpen(false);
            form.resetFields();
            fetchTeams(); // Refresh list
        } catch (error) {
            console.error("Failed to create team", error);
            message.error('Failed to create team');
        }
    };

    const columns = [
        {
            title: 'Team Name',
            dataIndex: 'name',
            key: 'name',
            render: (text, record) => <span style={{ fontWeight: 500 }}>{record.team_name || record.name}</span>
        },
        {
            title: 'Roles',
            key: 'roles',
            render: () => <span style={{ background: '#fff', padding: '4px 12px', borderRadius: 4, border: '1px solid #d9d9d9', fontSize: 12 }}>Member</span>
        },
        {
            title: 'Project ID',
            dataIndex: 'project_id',
            key: 'project_id',
            render: (pid) => pid ? `Project_${pid}` : 'None'
        },
        {
            title: 'Status',
            key: 'status',
            render: (_, record) => (
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: record.is_finalized ? '#ff4d4f' : '#52c41a' }} />
                    {record.is_finalized ? 'Finalized' : 'Active'}
                </span>
            )
        },
        {
            title: 'Action',
            key: 'action',
            render: (_, record) => (
                <Button
                    size="small"
                    shape="round"
                    onClick={() => navigate(`/teams/${record.team_id || record.id}`)}
                    style={{ border: '1px solid #d9d9d9' }}
                >
                    View
                </Button>
            )
        }
    ];
    const handleJoinTeam = async (values) => {
        try {
            await teamService.joinByCode(values.join_code);
            message.success('Joined team successfully');
            setIsJoinModalOpen(false);
            joinForm.resetFields();
            fetchTeams();
        } catch (error) {
            console.error("Failed to join team", error);
            message.error(error.response?.data?.detail || 'Failed to join team');
        }
    };

    return (
        <MainLayout>
            <div style={{ marginBottom: 30 }}>
                <Title level={2} style={{ margin: '0 0 8px 0', textTransform: 'uppercase', letterSpacing: 0.5 }}>Team Management</Title>
                <Text style={{ fontSize: 16, color: '#595959' }}>See your team and manage your team member and roles</Text>
            </div>

            <div style={{ display: 'flex', gap: 16, marginBottom: 40 }}>
                <Button
                    type="primary"
                    shape="round"
                    icon={<PlusOutlined />}
                    size="large"
                    onClick={() => setIsModalOpen(true)}
                    style={{ height: 46, padding: '0 32px', fontSize: 16, fontWeight: 500 }}
                >
                    Create Team
                </Button>
                <Button
                    shape="round"
                    icon={<TeamOutlined />}
                    size="large"
                    onClick={() => setIsJoinModalOpen(true)}
                    style={{ height: 46, padding: '0 32px', fontSize: 16, fontWeight: 500, background: '#e6e6e6', border: 'none', color: '#000' }}
                >
                    Join a Team
                </Button>
            </div>

            <div style={{ background: '#e6e6e6', borderRadius: 30, padding: 32, minHeight: 500 }}>
                <div style={{ marginBottom: 24 }}>
                    <Title level={3} style={{ margin: '0 0 4px 0' }}>Your Team</Title>
                    <Text style={{ fontSize: 14, color: '#595959' }}>Manage team members, roles</Text>
                </div>

                <Table
                    loading={loading}
                    dataSource={teams}
                    columns={columns}
                    rowKey={(record) => record.team_id || record.id || Math.random()}
                    pagination={false}
                    style={{ borderRadius: 16, overflow: 'hidden' }}
                />
            </div>

            <Modal
                title="Create New Team"
                open={isModalOpen}
                onCancel={() => setIsModalOpen(false)}
                onOk={() => form.submit()}
            >
                <Form form={form} layout="vertical" onFinish={handleCreateTeam}>
                    <Form.Item name="name" label="Team Name" rules={[{ required: true }]}>
                        <Input placeholder="Enter team name" />
                    </Form.Item>
                    <Form.Item name="description" label="Description">
                        <Input.TextArea placeholder="Team description" />
                    </Form.Item>
                </Form>
            </Modal>

            <Modal
                title="Join Team by Code"
                open={isJoinModalOpen}
                onCancel={() => setIsJoinModalOpen(false)}
                onOk={() => joinForm.submit()}
            >
                <Form form={joinForm} layout="vertical" onFinish={handleJoinTeam}>
                    <Form.Item
                        name="join_code"
                        label="Join Code"
                        rules={[{ required: true, message: 'Please enter a join code' }]}
                    >
                        <Input placeholder="Enter 8-character code" />
                    </Form.Item>
                </Form>
            </Modal>
        </MainLayout>
    );
};

export default TeamManagement;
