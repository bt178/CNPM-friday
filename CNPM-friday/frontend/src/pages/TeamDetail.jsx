import React, { useState, useEffect } from 'react';
import { Layout, Typography, Button, Descriptions, message, Card, List, Avatar, Space, Tag } from 'antd';
import { UserOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import { teamService } from '../services/api';

const { Title, Text } = Typography;
const { Content } = Layout;

const TeamDetail = () => {
    const { teamId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [team, setTeam] = useState(null);
    const [loading, setLoading] = useState(true);

    const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
    const [joinForm] = Form.useForm();
    const [isMember, setIsMember] = useState(false);
    const [isLeader, setIsLeader] = useState(false);

    const fetchTeamDetail = async () => {
        setLoading(true);
        try {
            const res = await teamService.getDetail(teamId);
            setTeam(res.data);
        } catch (error) {
            console.error("Failed to fetch team detail", error);
            message.error("Failed to load team detail");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (teamId) fetchTeamDetail();
    }, [teamId]);

    useEffect(() => {
        if (team && user) {
            // Check if user is leader
            setIsLeader(team.leader_id === user.user_id || team.leader_id === user.id);
            // Check if user is member
            const memberFound = team.members?.find(m => m.student_id === user.user_id || m.student_id === user.id || m.id === user.id);
            setIsMember(!!memberFound);
        }
    }, [team, user]);

    const handleJoinSubmit = async (values) => {
        try {
            await teamService.joinByCode(values.join_code);
            message.success("Joined team successfully");
            setIsJoinModalOpen(false);
            fetchTeamDetail();
        } catch (error) {
            message.error(error.response?.data?.detail || "Failed to join team");
        }
    };

    const handleLeave = async () => {
        try {
            await teamService.leave(teamId);
            message.success("Left team successfully");
            // Update state immediately for better UX
            setIsMember(false);
            fetchTeamDetail();
        } catch (error) {
            message.error(error.response?.data?.detail || "Failed to leave team");
        }
    };

    // ... (handleFinalize etc)

    return (
        <Layout style={{ minHeight: '100vh', padding: '24px' }}>
            <Content>
                <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/teams')} style={{ marginBottom: 16 }}>
                    Back to Teams
                </Button>

                <Card title={<Title level={3}>{team.name}</Title>} extra={
                    <Space>
                        {!isMember && (
                            <Button type="primary" onClick={() => setIsJoinModalOpen(true)}>Join Team</Button>
                        )}
                        {isMember && !isLeader && (
                            <Button danger onClick={handleLeave}>Leave Team</Button>
                        )}
                        {isLeader && (
                            <>
                                <Button onClick={handleFinalize} disabled={team.is_finalized}>Finalize</Button>
                                <Button onClick={handleSelectProject} disabled={team.is_finalized}>Select Project</Button>
                            </>
                        )}
                    </Space>
                }>
                    <Descriptions bordered column={1}>
                        <Descriptions.Item label="Description">{team.description || 'No description'}</Descriptions.Item>
                        <Descriptions.Item label="Project">{team.project?.title || 'None selected'}</Descriptions.Item>
                        <Descriptions.Item label="Status">{team.is_finalized ? <Tag color="red">Finalized</Tag> : <Tag color="green">Active</Tag>}</Descriptions.Item>

                        {/* Only Leader sees Join Code */}
                        {isLeader && !team.is_finalized && (
                            <Descriptions.Item label="Join Code">
                                <Text copyable strong style={{ fontSize: '16px', color: '#1890ff' }}>{team.join_code || 'N/A'}</Text>
                                <div style={{ fontSize: '12px', color: '#888' }}>Share this code with students you want to invite.</div>
                            </Descriptions.Item>
                        )}
                    </Descriptions>

                    <Title level={4} style={{ marginTop: 24 }}>Members</Title>
                    <List
                        itemLayout="horizontal"
                        dataSource={team.members || []}
                        renderItem={(member) => (
                            <List.Item>
                                <List.Item.Meta
                                    avatar={<Avatar icon={<UserOutlined />} src={member.avatar_url} />}
                                    title={member.full_name || member.name}
                                    description={member.email}
                                />
                                {member.role === 'Leader' ? <Tag color="gold">Leader</Tag> : <Tag>Member</Tag>}
                            </List.Item>
                        )}
                    />
                </Card>

                <Modal
                    title="Join Team"
                    open={isJoinModalOpen}
                    onCancel={() => setIsJoinModalOpen(false)}
                    onOk={() => joinForm.submit()}
                >
                    <Form form={joinForm} layout="vertical" onFinish={handleJoinSubmit}>
                        <Form.Item name="join_code" label="Enter Join Code" rules={[{ required: true }]}>
                            <Input placeholder="Team code..." />
                        </Form.Item>
                    </Form>
                </Modal>
            </Content>
        </Layout>
    );
};

export default TeamDetail;
