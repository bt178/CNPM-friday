// FE1 - Lecturer Dashboard & Topic Management
// Paste into src/pages/LecturerDashboard.jsx

import React, { useState, useEffect } from 'react';
import { Table, Button, Form, Modal, message, Space, Tag } from 'antd';
import { PlusOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import api from '../services/api';

export default function LecturerDashboard() {
    const [topics, setTopics] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();

    useEffect(() => {
        fetchTopics();
    }, []);

    const fetchTopics = async () => {
        setLoading(true);
        try {
            const response = await api.get('/topics');
            setTopics(response.data);
        } catch (error) {
            message.error('Failed to load topics');
        }
        setLoading(false);
    };

    const handleCreateTopic = async (values) => {
        try {
            await api.post('/topics', {
                title: values.title,
                description: values.description,
            });
            message.success('Topic created successfully');
            setIsModalVisible(false);
            form.resetFields();
            fetchTopics();
        } catch (error) {
            message.error(error.response?.data?.detail || 'Failed to create topic');
        }
    };

    const handleApprove = async (topicId) => {
        try {
            await api.patch(`/topics/${topicId}/approve`);
            message.success('Topic approved');
            fetchTopics();
        } catch (error) {
            message.error('Failed to approve topic');
        }
    };

    const handleReject = async (topicId) => {
        try {
            await api.patch(`/topics/${topicId}/reject`);
            message.success('Topic rejected');
            fetchTopics();
        } catch (error) {
            message.error('Failed to reject topic');
        }
    };

    const columns = [
        {
            title: 'Title',
            dataIndex: 'title',
            key: 'title',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status) => {
                const color = status === 'APPROVED' ? 'green' : status === 'DRAFT' ? 'orange' : 'red';
                return <Tag color={color}>{status}</Tag>;
            },
        },
        {
            title: 'Description',
            dataIndex: 'description',
            key: 'description',
            width: 300,
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    {record.status === 'DRAFT' && (
                        <>
                            <Button
                                type="primary"
                                size="small"
                                icon={<CheckOutlined />}
                                onClick={() => handleApprove(record.topic_id)}
                            >
                                Approve
                            </Button>
                            <Button
                                danger
                                size="small"
                                icon={<CloseOutlined />}
                                onClick={() => handleReject(record.topic_id)}
                            >
                                Reject
                            </Button>
                        </>
                    )}
                </Space>
            ),
        },
    ];

    return (
        <div style={{ padding: '24px' }}>
            <h1>Topics Management</h1>
            <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setIsModalVisible(true)}
                style={{ marginBottom: '16px' }}
            >
                Create Topic
            </Button>

            <Table
                columns={columns}
                dataSource={topics.map(t => ({ ...t, key: t.topic_id }))}
                loading={loading}
                pagination={{ pageSize: 10 }}
            />

            <Modal
                title="Create New Topic"
                visible={isModalVisible}
                onOk={() => form.submit()}
                onCancel={() => setIsModalVisible(false)}
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleCreateTopic}
                >
                    <Form.Item
                        label="Title"
                        name="title"
                        rules={[{ required: true, message: 'Please enter topic title' }]}
                    >
                        <input type="text" placeholder="Topic title" />
                    </Form.Item>
                    <Form.Item label="Description" name="description">
                        <textarea placeholder="Topic description" rows={4} />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
}
