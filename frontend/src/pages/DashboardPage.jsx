import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Layout, Typography, Button, Card, Row, Col, Progress, List,
    Avatar, Space, Badge, Input, Upload, Timeline, Tag, Divider,
    Modal, Form, Select, DatePicker, message, Dropdown, Popover
} from 'antd';
import {
    SettingOutlined, BellOutlined, SearchOutlined, PlusOutlined,
    DashboardOutlined, TeamOutlined, DesktopOutlined, TableOutlined,
    FileTextOutlined, VideoCameraOutlined, SendOutlined, FormOutlined,
    LogoutOutlined, UserOutlined, FilePdfOutlined,
    FileImageOutlined, FileOutlined, ClockCircleOutlined, UploadOutlined,
    MoreOutlined, CheckCircleOutlined, SyncOutlined, PlayCircleOutlined,
    FolderOutlined, CloudUploadOutlined, CalendarOutlined, ProjectOutlined,
    LeftOutlined, RightOutlined, DeleteOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { useAuth, resolveRoleName } from '../components/AuthContext';
import './DashboardPage.css';

const { Title, Text } = Typography;
const { Header, Sider, Content } = Layout;

const STORAGE_BASE_KEYS = {
    avatar: 'user_avatar',
};

const LEGACY_KEYS = {
    avatar: 'user_avatar',
};

const canUseStorage = () => typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';

const buildScopedKey = (baseKey, user) => {
    const identifier = user?.id || user?.email;
    return identifier ? `${baseKey}_${identifier}` : `${baseKey}_default`;
};

const readScopedAvatar = (storageKey, fallback) => {
    if (!canUseStorage() || !storageKey) {
        return fallback;
    }
    const scopedValue = window.localStorage.getItem(storageKey);
    return scopedValue || fallback;
};

const readScopedProfile = (storageKey, user) => {
    if (!canUseStorage() || !storageKey) {
        return null;
    }
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) {
        return null;
    }
    try {
        const parsed = JSON.parse(raw);
        if (parsed?._owner && user?.email && parsed._owner !== user.email) {
            return null;
        }
        return parsed;
    } catch (_err) {
        return null;
    }
};

const readActiveProjectsPayload = (storageKey, user) => {
    if (!canUseStorage()) {
        return [];
    }
    const scopedRaw = storageKey ? window.localStorage.getItem(storageKey) : null;
    const raw = scopedRaw || window.localStorage.getItem('active_projects');
    if (!raw) {
        return [];
    }
    try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
            return parsed;
        }
        if (parsed && Array.isArray(parsed.items)) {
            if (!scopedRaw && parsed._owner && user?.email && parsed._owner !== user.email) {
                return [];
            }
            return parsed.items;
        }
        return [];
    } catch (_err) {
        return [];
    }
};

const getProjectIcon = (project) => {
    if (React.isValidElement(project.icon)) {
        return project.icon;
    }
    if (project.iconType === 'project') {
        return <ProjectOutlined />;
    }
    return <ProjectOutlined />;
};

const ProjectDashboard = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const [collapsed, setCollapsed] = useState(false);
    const [isNotificationOpen, setNotificationOpen] = useState(false);
    const notificationAnchorRef = useRef(null);
    const profileStorageKey = useMemo(() => buildScopedKey('user_profile', user), [user]);
    const avatarStorageKey = useMemo(() => buildScopedKey(STORAGE_BASE_KEYS.avatar, user), [user]);
    const activeProjectsStorageKey = useMemo(() => buildScopedKey('active_projects', user), [user]);
    const [avatarUrl, setAvatarUrl] = useState(() => readScopedAvatar(avatarStorageKey, user?.avatar_url || null));
    const [profileSnapshot, setProfileSnapshot] = useState(() => {
        const scoped = readScopedProfile(profileStorageKey, user);
        if (scoped) {
            return scoped;
        }
        if (!canUseStorage()) {
            return null;
        }
        const raw = window.localStorage.getItem('user_profile');
        if (!raw) {
            return null;
        }
        try {
            const parsed = JSON.parse(raw);
            if (parsed?._owner && user?.email && parsed._owner !== user.email) {
                return null;
            }
            return parsed;
        } catch (_err) {
            return null;
        }
    });

    useEffect(() => {
        if (!canUseStorage()) {
            return;
        }
        window.localStorage.removeItem(LEGACY_KEYS.avatar);
    }, []);

    useEffect(() => {
        setAvatarUrl(readScopedAvatar(avatarStorageKey, user?.avatar_url || null));
    }, [avatarStorageKey, user?.avatar_url]);

    useEffect(() => {
        const handleAvatarUpdated = () => {
            setAvatarUrl(readScopedAvatar(avatarStorageKey, user?.avatar_url || null));
        };

        window.addEventListener('avatar-updated', handleAvatarUpdated);
        window.addEventListener('storage', handleAvatarUpdated);
        return () => {
            window.removeEventListener('avatar-updated', handleAvatarUpdated);
            window.removeEventListener('storage', handleAvatarUpdated);
        };
    }, [avatarStorageKey, user?.avatar_url]);

    useEffect(() => {
        const scopedProfile = readScopedProfile(profileStorageKey, user);
        if (scopedProfile) {
            setProfileSnapshot(scopedProfile);
            return;
        }
        if (!canUseStorage()) {
            setProfileSnapshot(null);
            return;
        }
        const raw = window.localStorage.getItem('user_profile');
        if (!raw) {
            setProfileSnapshot(null);
            return;
        }
        try {
            const parsed = JSON.parse(raw);
            if (parsed?._owner && user?.email && parsed._owner !== user.email) {
                setProfileSnapshot(null);
                return;
            }
            setProfileSnapshot(parsed);
        } catch (_err) {
            setProfileSnapshot(null);
        }
    }, [profileStorageKey, user?.full_name, user?.email]);

    useEffect(() => {
        const handleProfileUpdated = () => {
            const scopedProfile = readScopedProfile(profileStorageKey, user);
            if (scopedProfile) {
                setProfileSnapshot(scopedProfile);
                return;
            }
            if (!canUseStorage()) {
                return;
            }
            const raw = window.localStorage.getItem('user_profile');
            if (!raw) {
                setProfileSnapshot(null);
                return;
            }
            try {
                const parsed = JSON.parse(raw);
                if (parsed?._owner && user?.email && parsed._owner !== user.email) {
                    setProfileSnapshot(null);
                    return;
                }
                setProfileSnapshot(parsed);
            } catch (_err) {
                setProfileSnapshot(null);
            }
        };

        window.addEventListener('profile-updated', handleProfileUpdated);
        window.addEventListener('storage', handleProfileUpdated);
        return () => {
            window.removeEventListener('profile-updated', handleProfileUpdated);
            window.removeEventListener('storage', handleProfileUpdated);
        };
    }, [profileStorageKey, user]);

    useEffect(() => {
        if (!canUseStorage() || !avatarStorageKey) {
            return;
        }
        if (avatarUrl) {
            window.localStorage.setItem(avatarStorageKey, avatarUrl);
        } else {
            window.localStorage.removeItem(avatarStorageKey);
        }
    }, [avatarUrl, avatarStorageKey]);
    const greetingName = useMemo(() => {
        const fallback = user?.email || 'there';
        const source = profileSnapshot?.name || user?.full_name || fallback;
        const parts = source.trim().split(' ').filter(Boolean);
        return parts.length ? parts[parts.length - 1] : source;
    }, [profileSnapshot?.name, user]);
    const [currentDate, setCurrentDate] = useState(dayjs());
    const [isEventModalOpen, setEventModalOpen] = useState(false);
    const [eventForm] = Form.useForm();
    const [totalFiles, setTotalFiles] = useState(124);
    const [storageUsage, setStorageUsage] = useState(65);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [hoveredNav, setHoveredNav] = useState(null);

    const navButtonStyles = (key, { active, danger } = {}) => ({
        textAlign: collapsed ? 'center' : 'left',
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'flex-start',
        borderRadius: 8,
        padding: collapsed ? '8px 0' : '8px 12px',
        color: danger ? '#d4380d' : active ? '#1890ff' : '#595959',
        fontWeight: active ? 600 : 500,
        backgroundColor: hoveredNav === key ? 'rgba(24, 144, 255, 0.08)' : 'transparent',
        transform: hoveredNav === key && !collapsed ? 'translateX(2px)' : 'none',
        transition: 'all 0.2s ease',
    });

    const navButtonInteractions = (key, options) => ({
        style: navButtonStyles(key, options),
        onMouseEnter: () => setHoveredNav(key),
        onMouseLeave: () => setHoveredNav(null),
    });

    const hamburgerLineBase = {
        width: 18,
        height: 2,
        backgroundColor: '#262626',
        display: 'block',
        borderRadius: 2,
        transition: 'transform 0.3s ease, opacity 0.3s ease',
    };

    const hamburgerLineStyle = (position) => {
        if (collapsed) {
            switch (position) {
                case 'top':
                    return { ...hamburgerLineBase, transform: 'translateY(0) rotate(0)' };
                case 'middle':
                    return { ...hamburgerLineBase, opacity: 1 };
                case 'bottom':
                default:
                    return { ...hamburgerLineBase, transform: 'translateY(0) rotate(0)' };
            }
        }
        switch (position) {
            case 'top':
                return { ...hamburgerLineBase, transform: 'translateY(6px) rotate(45deg)' };
            case 'middle':
                return { ...hamburgerLineBase, opacity: 0 };
            case 'bottom':
            default:
                return { ...hamburgerLineBase, transform: 'translateY(-6px) rotate(-45deg)' };
        }
    };

    // Determine Role
    const userRole = useMemo(() => {
        const rawRole = resolveRoleName(user) || 'Student'; // Fallback
        // Normalize for display: "HEAD_DEPT" -> "Head Dept"
        return rawRole
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }, [user]);

    // Role-based Data
    const roleBasedProjects = useMemo(() => {
        const roleUpper = userRole.toUpperCase();
        if (roleUpper === 'STUDENT') {
            return [
                { id: 1, title: 'Introduction to AI', description: 'Complete the weekly assignments and quiz', icon: <PlayCircleOutlined /> },
                { id: 2, title: 'Web Development', description: 'Build a personal portfolio website', icon: <PlayCircleOutlined /> },
                { id: 3, title: 'Database Systems', description: 'Design a relational database schema', icon: <PlayCircleOutlined /> },
            ];
        } else if (roleUpper === 'LECTURER' || roleUpper === 'ADMIN' || roleUpper === 'STAFF') {
            return [
                { id: 1, title: 'AI Course Grading', description: 'Grade the midterm submissions', icon: <PlayCircleOutlined /> },
                { id: 2, title: 'Curriculum Review', description: 'Update the syllabus for next semester', icon: <PlayCircleOutlined /> },
                { id: 3, title: 'Research Grant', description: 'Prepare proposal for research funding', icon: <PlayCircleOutlined /> },
                { id: 4, title: 'Department Meeting', description: 'Weekly sync with faculty members', icon: <PlayCircleOutlined /> },
            ];
        }
        return [
            { id: 1, title: 'Project A', description: 'Website redesign with improved UX and responsive layout', icon: <PlayCircleOutlined /> },
            { id: 2, title: 'Project B', description: 'Mobile app development for campus navigation', icon: <PlayCircleOutlined /> },
            { id: 3, title: 'Project C', description: 'AI-powered learning assistant system', icon: <PlayCircleOutlined /> },
            { id: 4, title: 'Project D', description: 'E-commerce platform optimization', icon: <PlayCircleOutlined /> },
        ];
    }, [userRole]);

    const roleBasedTimeline = useMemo(() => {
        const roleUpper = userRole.toUpperCase();
        if (roleUpper === 'STUDENT') {
            return [
                { id: 101, date: 'Nov. 10, 2025', project: 'Intro to AI', description: 'Submitted Assignment 1', status: 'completed' },
                { id: 102, date: 'Nov. 12, 2025', project: 'Web Dev', description: 'Started working on Portfolio', status: 'in-progress' },
                { id: 103, date: 'Nov. 15, 2025', project: 'Database', description: 'Quiz 2 due', status: 'pending' },
            ];
        } else if (roleUpper === 'LECTURER' || roleUpper === 'ADMIN' || roleUpper === 'STAFF') {
            return [
                { id: 101, date: 'Nov. 10, 2025', project: 'AI Grading', description: 'Completed grading for section A', status: 'completed' },
                { id: 102, date: 'Nov. 12, 2025', project: 'Curriculum', description: 'Drafted new module', status: 'in-progress' },
                { id: 103, date: 'Nov. 15, 2025', project: 'Meeting', description: 'Faculty board meeting', status: 'pending' },
            ];
        }
        return [
            { id: 101, date: 'Nov. 10, 2025', project: 'Project A', description: 'Project kickoff meeting and requirements gathering', status: 'completed' },
            { id: 102, date: 'Nov. 12, 2025', project: 'Project B', description: 'Initial design review and feedback session', status: 'in-progress' },
            { id: 103, date: 'Nov. 15, 2025', project: 'Project C', description: 'Development sprint planning and task assignment', status: 'pending' },
            { id: 104, date: 'Nov. 17, 2025', project: 'Project D', description: 'Client presentation and milestone review', status: 'in-progress' },
            { id: 105, date: 'Nov. 20, 2025', project: 'Project A', description: 'User testing phase begins', status: 'pending' },
        ];
    }, [userRole]);


    // Active Projects Data
    const [activeProjects, setActiveProjects] = useState(() => {
        const stored = readActiveProjectsPayload(activeProjectsStorageKey, user);
        return [...roleBasedProjects, ...stored].reduce((acc, item) => {
            const id = String(item.id ?? item.title ?? Math.random());
            if (acc.some((existing) => String(existing.id ?? existing.title) === id)) {
                return acc;
            }
            acc.push(item);
            return acc;
        }, []);
    });

    // Update state when role changes
    useEffect(() => {
        const stored = readActiveProjectsPayload(activeProjectsStorageKey, user);
        const merged = [...roleBasedProjects, ...stored].reduce((acc, item) => {
            const id = String(item.id ?? item.title ?? Math.random());
            if (acc.some((existing) => String(existing.id ?? existing.title) === id)) {
                return acc;
            }
            acc.push(item);
            return acc;
        }, []);
        setActiveProjects(merged);
    }, [roleBasedProjects, activeProjectsStorageKey, user]);

    useEffect(() => {
        const handleActiveProjectsUpdate = () => {
            const stored = readActiveProjectsPayload(activeProjectsStorageKey, user);
            const merged = [...roleBasedProjects, ...stored].reduce((acc, item) => {
                const id = String(item.id ?? item.title ?? Math.random());
                if (acc.some((existing) => String(existing.id ?? existing.title) === id)) {
                    return acc;
                }
                acc.push(item);
                return acc;
            }, []);
            setActiveProjects(merged);
        };

        window.addEventListener('active-projects-updated', handleActiveProjectsUpdate);
        window.addEventListener('storage', handleActiveProjectsUpdate);
        return () => {
            window.removeEventListener('active-projects-updated', handleActiveProjectsUpdate);
            window.removeEventListener('storage', handleActiveProjectsUpdate);
        };
    }, [activeProjectsStorageKey, roleBasedProjects, user]);

    // Timeline Data
    const [timelineData, setTimelineData] = useState(roleBasedTimeline);

    // Update state when role changes
    useEffect(() => {
        setTimelineData(roleBasedTimeline);
    }, [roleBasedTimeline]);

    // Recent Files Data
    const [recentFiles, setRecentFiles] = useState([
        { name: 'Test_report_2025.pdf', size: '1.0 MB', time: '2h ago', icon: <FilePdfOutlined />, type: 'PDF' },
        { name: 'Mockup.fig', size: '4.2 MB', time: '2h ago', icon: <FileImageOutlined />, type: 'Design' },
        { name: 'Requirements.docx', size: '1.1 MB', time: '1d ago', icon: <FileOutlined />, type: 'Document' },
        { name: 'Design_specs.pdf', size: '3.5 MB', time: '1d ago', icon: <FilePdfOutlined />, type: 'PDF' },
        { name: 'Wireframes.xd', size: '2.8 MB', time: '2d ago', icon: <FileImageOutlined />, type: 'Design' },
        { name: 'Backend_api.json', size: '0.8 MB', time: '3d ago', icon: <FileOutlined />, type: 'JSON' },
    ]);

    const notifications = useMemo(() => ([
        {
            id: 1,
            title: 'New Task Assigned',
            description: 'You have been assigned a new task titled "Complete Project Report."',
            timeAgo: '10 minutes ago',
        },
        {
            id: 2,
            title: 'Deadline Warning',
            description: "Reminder: The deadline for the task 'Submit Proposal' is approaching.",
            timeAgo: '10 minutes ago',
        },
        {
            id: 3,
            title: 'New Message Received',
            description: 'You have a new message from Test user.',
            timeAgo: '10 minutes ago',
        },
    ]), []);

    const notificationContent = (
        <div style={{ width: 320 }}>
            <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 8 }}>Notifications</div>
            <Divider style={{ margin: '0 0 12px' }} />
            <div>
                {notifications.map((item, index) => (
                    <div key={item.id} style={{ padding: '8px 0' }}>
                        <div style={{ display: 'flex', gap: 12 }}>
                            <Avatar shape="square" size={36} style={{ backgroundColor: '#f0f0f0', color: '#8c8c8c' }}>
                                <BellOutlined />
                            </Avatar>
                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
                                        <Text strong style={{ display: 'block' }}>{item.title}</Text>
                                        <Text type="secondary" style={{ fontSize: 12 }}>{item.description}</Text>
                                    </div>
                                    <Text type="secondary" style={{ fontSize: 11 }}>{item.timeAgo}</Text>
                                </div>
                            </div>
                        </div>
                        {index !== notifications.length - 1 && <Divider style={{ margin: '12px 0' }} />}
                    </div>
                ))}
            </div>
            <Divider style={{ margin: '8px 0 12px' }} />
            <Button type="link" block onClick={() => setNotificationOpen(false)}>
                View all Notifications
            </Button>
        </div>
    );

    const formatFileSize = (bytes = 0) => {
        if (!bytes) {
            return '0 MB';
        }
        const mb = bytes / (1024 * 1024);
        return `${mb < 1 ? (mb * 1024).toFixed(0) + ' KB' : mb.toFixed(1) + ' MB'}`;
    };

    const resolveFileDisplay = (fileName = '') => {
        const ext = fileName.split('.').pop()?.toLowerCase();
        switch (ext) {
            case 'pdf':
                return { type: 'PDF', icon: <FilePdfOutlined /> };
            case 'fig':
            case 'xd':
            case 'png':
            case 'jpg':
            case 'jpeg':
                return { type: 'Design', icon: <FileImageOutlined /> };
            case 'doc':
            case 'docx':
            case 'txt':
                return { type: 'Document', icon: <FileOutlined /> };
            case 'json':
            case 'csv':
                return { type: 'JSON', icon: <FileOutlined /> };
            default:
                return { type: ext ? ext.toUpperCase() : 'FILE', icon: <FileOutlined /> };
        }
    };

    const handleFileUpload = (file) => {
        const { type, icon } = resolveFileDisplay(file.name);
        const uploadedFile = {
            id: Date.now(),
            name: file.name,
            size: formatFileSize(file.size),
            time: 'just now',
            icon,
            type,
        };
        setUploadedFiles((prev) => [uploadedFile, ...prev]);
        setTotalFiles((prev) => prev + 1);
        setStorageUsage((prev) => Math.min(100, prev + 2));
        message.success(`${file.name} uploaded`);
        return false;
    };

    const handleRemoveUploadedFile = (fileId) => {
        setUploadedFiles((prev) => prev.filter((file) => file.id !== fileId));
        setTotalFiles((prev) => Math.max(0, prev - 1));
        message.success('File removed');
    };

    // Recent Activities Data
    const recentActivities = [
        'Smart Inventory System',
        'AI Health Monitor',
        'Smart Campus App',
        'Drone Delivery'
    ];

    // Calendar Logic
    const startDay = currentDate.startOf('month').day();
    const daysInMonth = currentDate.daysInMonth();
    const daysArray = Array.from({ length: daysInMonth }, (_, i) => i + 1);
    const emptyDays = Array.from({ length: startDay }, (_, i) => i);

    const nextMonth = () => setCurrentDate(currentDate.add(1, 'month'));
    const prevMonth = () => setCurrentDate(currentDate.subtract(1, 'month'));

    const getStatusTag = (status) => {
        switch (status) {
            case 'completed': return <Tag color="green" icon={<CheckCircleOutlined />}>Completed</Tag>;
            case 'in-progress': return <Tag color="blue" icon={<SyncOutlined spin />}>In Progress</Tag>;
            default: return <Tag color="orange">Pending</Tag>;
        }
    };



    const handleEventSubmit = (values) => {
        const newEvent = {
            date: values.date ? values.date.format('MMM. DD, YYYY') : dayjs().format('MMM. DD, YYYY'),
            project: values.project,
            description: values.description,
            status: values.status,
            id: Date.now(),
        };
        setTimelineData((prev) => [newEvent, ...prev]);
        message.success('Event added');
        setEventModalOpen(false);
        eventForm.resetFields();
    };

    const deleteProject = (id) => {
        setActiveProjects((prev) => prev.filter((project) => project.id !== id));
        if (canUseStorage() && activeProjectsStorageKey) {
            const stored = readActiveProjectsPayload(activeProjectsStorageKey, user);
            const nextItems = stored.filter((project) => String(project.id) !== String(id));
            const payload = { _owner: user?.email || null, items: nextItems };
            window.localStorage.setItem(activeProjectsStorageKey, JSON.stringify(payload));
            window.localStorage.setItem('active_projects', JSON.stringify(payload));
            window.dispatchEvent(new CustomEvent('active-projects-updated', { detail: { items: nextItems } }));
        }
        message.success('Project removed');
    };

    const deleteEvent = (id) => {
        setTimelineData((prev) => prev.filter((event) => event.id !== id));
        message.success('Event removed');
    };

    return (
        <Layout className="dashboard-layout" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
            {/* Fixed Header */}
            <Header className="dashboard-header" style={{
                position: 'fixed',
                top: 0,
                zIndex: 1000,
                width: '100%',
                background: '#fff',
                display: 'flex',
                justifyContent: 'space-between',
                padding: '0 24px',
                borderBottom: '1px solid #f0f0f0',
                height: '64px',
                lineHeight: '64px',
            }}>
                <Space size="large">
                    <Avatar size="small" style={{ backgroundColor: '#1890ff' }}>C</Avatar>
                    <Text strong style={{ fontSize: '16px' }}>CollabSphere</Text>
                </Space>
                <Space size="large">
                    <div ref={notificationAnchorRef} style={{ display: 'inline-flex' }}>
                        <Popover
                            content={notificationContent}
                            trigger="click"
                            placement="bottomRight"
                            open={isNotificationOpen}
                            onOpenChange={setNotificationOpen}
                            overlayStyle={{ padding: 0 }}
                            arrowPointAtCenter
                            getPopupContainer={() => notificationAnchorRef.current || document.body}
                        >
                            <Badge dot offset={[-5, 5]}>
                                <BellOutlined style={{ fontSize: 20, color: '#000', cursor: 'pointer' }} />
                            </Badge>
                        </Popover>
                    </div>
                    <Input
                        placeholder="Search..."
                        prefix={<SearchOutlined />}
                        style={{ width: 200, borderRadius: '6px' }}
                    />
                </Space>
            </Header>

            <Layout style={{ marginTop: '64px', height: 'calc(100vh - 64px)', background: '#f5f5f5' }}>
                {/* Fixed Left Sidebar */}
                <Sider
                    className="dashboard-sider"
                    width={240}
                    theme="light"
                    style={{
                        borderRight: '1px solid #f0f0f0',
                        height: 'calc(100vh - 64px)',
                        overflow: 'hidden',
                        position: 'fixed',
                        left: 0,
                        top: '64px',
                        background: '#ffffff',
                        boxShadow: '6px 0 18px rgba(15, 18, 21, 0.04)'
                    }}
                    collapsible
                    collapsed={collapsed}
                    trigger={null}
                >
                    <div style={{ padding: collapsed ? '24px 8px' : '24px 24px 0', display: 'flex', flexDirection: 'column', height: '100%' }}>
                        <div style={{ marginBottom: 24, paddingLeft: collapsed ? 12 : 0 }}>
                            <button
                                type="button"
                                onClick={() => setCollapsed(!collapsed)}
                                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                                style={{
                                    border: '1px solid #f0f0f0',
                                    borderRadius: 12,
                                    width: 40,
                                    height: 36,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    cursor: 'pointer',
                                    background: '#fff',
                                    transition: 'box-shadow 0.3s ease',
                                }}
                                onMouseEnter={(event) => {
                                    event.currentTarget.style.boxShadow = '0 6px 18px rgba(0,0,0,0.08)';
                                }}
                                onMouseLeave={(event) => {
                                    event.currentTarget.style.boxShadow = 'none';
                                }}
                            >
                                <span style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                    <span style={hamburgerLineStyle('top')} />
                                    <span style={hamburgerLineStyle('middle')} />
                                    <span style={hamburgerLineStyle('bottom')} />
                                </span>
                            </button>
                        </div>

                        {/* User Info Section */}
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32, justifyContent: collapsed ? 'center' : 'flex-start', flexDirection: collapsed ? 'column' : 'row' }}>
                            <Avatar size={collapsed ? 40 : 64} src={avatarUrl} style={{ backgroundColor: '#d9d9d9', marginRight: collapsed ? 0 : 16 }} />
                            {!collapsed && (
                                <div>
                                    <Title level={4} style={{ margin: 0, fontWeight: 'normal' }}>Hi <span style={{ color: '#1890ff' }}>{greetingName}</span>!</Title>
                                    <Text type="secondary">{userRole}</Text>
                                </div>
                            )}
                        </div>

                        {/* Navigation Menu */}
                        <div style={{ marginBottom: 16 }}>
                            {!collapsed && <Text strong style={{ color: '#1890ff', fontSize: '12px', letterSpacing: '1px' }}>OVERVIEW</Text>}
                            <Space direction="vertical" style={{ width: '100%', marginTop: 16 }} size={8}>
                                <Button
                                    type="text"
                                    block
                                    icon={<DashboardOutlined />}
                                    {...navButtonInteractions('dashboard', { active: true })}
                                >
                                    {!collapsed && "Dashboard"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<TeamOutlined />}
                                    {...navButtonInteractions('team')}
                                >
                                    {!collapsed && "Team Management"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<DesktopOutlined />}
                                    {...navButtonInteractions('workspace')}
                                >
                                    {!collapsed && "Real-time Workspace"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<TableOutlined />}
                                    {...navButtonInteractions('kanban')}
                                >
                                    {!collapsed && "Kanban Board Detail"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<FormOutlined />}
                                    {...navButtonInteractions('whiteboard')}
                                >
                                    {!collapsed && "Whiteboard Canvas"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<VideoCameraOutlined />}
                                    {...navButtonInteractions('video')}
                                >
                                    {!collapsed && "Video Meeting Room"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<SendOutlined />}
                                    {...navButtonInteractions('submission')}
                                >
                                    {!collapsed && "Submission Portal"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<FileTextOutlined />}
                                    {...navButtonInteractions('peer')}
                                >
                                    {!collapsed && "Peer Review Form"}
                                </Button>
                            </Space>
                        </div>

                        {/* Spacer to position settings slightly lower */}
                        <div style={{ height: collapsed ? 12 : 200 }} />

                        {/* Settings Section */}
                        <div>
                            {!collapsed && <Text strong style={{ color: '#1890ff', fontSize: '12px', letterSpacing: '1px' }}>SETTINGS</Text>}
                            <Space direction="vertical" style={{ width: '100%', marginTop: 16 }} size={8}>
                                <Button
                                    type="text"
                                    block
                                    icon={<SettingOutlined />}
                                    onClick={() => navigate('/profile')}
                                    {...navButtonInteractions('settings')}
                                >
                                    {!collapsed && "Settings"}
                                </Button>
                                <Button
                                    type="text"
                                    block
                                    icon={<LogoutOutlined />}
                                    onClick={logout}
                                    {...navButtonInteractions('logout', { danger: true })}
                                >
                                    {!collapsed && "Logout"}
                                </Button>
                            </Space>
                        </div>
                    </div>
                </Sider>

                {/* Main Content */}
                <Content className="dashboard-content" style={{
                    marginLeft: collapsed ? '80px' : '240px',
                    marginRight: '300px',
                    padding: '24px',
                    background: '#f5f5f5',
                    minHeight: 'calc(100vh - 64px)'
                }}>
                    {/* TOP SECTION: Active Projects and Timeline */}
                    <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
                        {/* Active Projects Box */}
                        <Col span={12}>
                            <Card
                                className="dashboard-card project-card"
                                title={
                                    <Space>
                                        <ProjectOutlined style={{ color: '#52c41a', fontSize: '18px' }} />
                                        <Text strong style={{ fontSize: '16px' }}>Active Projects ({activeProjects.length})</Text>
                                    </Space>
                                }
                                extra={
                                    <Button type="text" icon={<RightOutlined />} size="small" onClick={() => navigate('/projects')}>
                                        View Projects
                                    </Button>
                                }
                                style={{ height: '100%', borderRadius: '12px', boxShadow: '0 20px 60px rgba(15, 18, 21, 0.06)' }}
                            >
                                <div style={{
                                    maxHeight: '55vh',
                                    overflowY: activeProjects.length > 6 ? 'auto' : 'visible',
                                    paddingRight: activeProjects.length > 6 ? 8 : 0
                                }}>
                                    <List
                                        dataSource={activeProjects}
                                        renderItem={(project) => (
                                            <List.Item
                                                style={{
                                                    padding: '16px 0',
                                                    borderBottom: '1px solid #f0f0f0',
                                                    transition: 'all 0.3s'
                                                }}
                                                className="project-item"
                                            >
                                                <List.Item.Meta
                                                    avatar={
                                                        <div style={{
                                                            backgroundColor: '#f6ffed',
                                                            borderRadius: '8px',
                                                            padding: '8px',
                                                            color: '#52c41a'
                                                        }}>
                                                            {getProjectIcon(project)}
                                                        </div>
                                                    }
                                                    title={<Text strong style={{ fontSize: '14px' }}>{project.title}</Text>}
                                                    description={
                                                        <Text type="secondary" style={{ fontSize: '12px' }}>
                                                            {project.description}
                                                        </Text>
                                                    }
                                                />
                                                <Dropdown
                                                    menu={{
                                                        items: [
                                                            {
                                                                key: 'remove',
                                                                label: 'Remove',
                                                                icon: <DeleteOutlined />,
                                                                onClick: () => deleteProject(project.id),
                                                            },
                                                        ],
                                                    }}
                                                    trigger={['click']}
                                                >
                                                    <Button size="small" type="text" icon={<MoreOutlined />} />
                                                </Dropdown>
                                            </List.Item>
                                        )}
                                    />
                                </div>
                            </Card>
                        </Col>

                        {/* Timeline Box */}
                        <Col span={12}>
                            <Card
                                className="dashboard-card timeline-card"
                                title={
                                    <Space>
                                        <CalendarOutlined style={{ color: '#1890ff', fontSize: '18px' }} />
                                        <Text strong style={{ fontSize: '16px' }}>Project Timeline (5)</Text>
                                    </Space>
                                }
                                extra={
                                    <Button type="text" icon={<PlusOutlined />} size="small" onClick={() => setEventModalOpen(true)}>
                                        Add Event
                                    </Button>
                                }
                                style={{ height: '100%', borderRadius: '12px', boxShadow: '0 20px 60px rgba(15, 18, 21, 0.06)' }}
                            >
                                <div className="timeline-scroll-container">
                                    <Timeline className="timeline-list">
                                        {timelineData.map((item, index) => (
                                            <Timeline.Item color={index % 2 === 0 ? 'blue' : 'green'} key={item.id}>
                                                <div className="timeline-event">
                                                    <div className="timeline-event__content">
                                                        <div className="timeline-event__details">
                                                            <Text strong style={{ fontSize: '12px', color: '#666' }}>{item.date}</Text>
                                                            <div style={{ marginTop: '4px' }}>
                                                                <Text strong style={{ fontSize: '14px' }}>{item.project}</Text>
                                                                <div style={{ marginTop: '2px' }}>
                                                                    <Text type="secondary" style={{ fontSize: '12px' }}>
                                                                        {item.description}
                                                                    </Text>
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <Space size="small" className="timeline-event__actions">
                                                            {getStatusTag(item.status)}
                                                            <Dropdown
                                                                menu={{
                                                                    items: [
                                                                        {
                                                                            key: 'remove',
                                                                            label: 'Remove',
                                                                            icon: <DeleteOutlined />,
                                                                            onClick: () => deleteEvent(item.id),
                                                                        },
                                                                    ],
                                                                }}
                                                                trigger={['click']}
                                                            >
                                                                <Button size="small" type="text" icon={<MoreOutlined />} />
                                                            </Dropdown>
                                                        </Space>
                                                    </div>
                                                </div>
                                            </Timeline.Item>
                                        ))}
                                    </Timeline>
                                </div>
                            </Card>
                        </Col>
                    </Row>

                    {/* BOTTOM SECTION: Files */}
                    <Card
                        className="dashboard-card files-card"
                        title={
                            <Space>
                                <FolderOutlined style={{ color: '#722ed1', fontSize: '18px' }} />
                                <Text strong style={{ fontSize: '16px' }}>Files & Documents</Text>
                            </Space>
                        }
                        extra={
                            <Space>
                                <Button type="text" size="small">
                                    View All Files
                                </Button>
                                <Upload
                                    beforeUpload={handleFileUpload}
                                    showUploadList={false}
                                    accept=".pdf,.doc,.docx,.json,.csv,.fig,.xd,.png,.jpg,.jpeg"
                                >
                                    <Button type="primary" icon={<CloudUploadOutlined />} size="small">
                                        Upload Files
                                    </Button>
                                </Upload>
                            </Space>
                        }
                        style={{
                            borderRadius: 20,
                            boxShadow: '0 28px 65px rgba(15, 18, 21, 0.08)',
                            border: '1px solid #ffffff',
                            background: '#ffffff'
                        }}
                        bodyStyle={{ background: '#ffffff' }}
                    >
                        {/* Files Stats Row */}
                        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                            <Col span={6}>
                                <Card
                                    size="small"
                                    className="file-stat-card file-stat-card--total"
                                    style={{ background: '#f9f0ff', border: 'none', borderRadius: '6px' }}
                                >
                                    <div style={{ textAlign: 'center' }}>
                                        <Text strong style={{ fontSize: '24px', color: '#722ed1' }}>{totalFiles}</Text>
                                        <div>
                                            <Text type="secondary" style={{ fontSize: '12px' }}>Total Files</Text>
                                        </div>
                                    </div>
                                </Card>
                            </Col>
                            <Col span={12}>
                                <Card
                                    size="small"
                                    className="file-stat-card"
                                    style={{ border: 'none', borderRadius: '6px' }}
                                >
                                    <div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <Text strong>Storage Usage</Text>
                                            <Text strong>{storageUsage}%</Text>
                                        </div>
                                        <Progress percent={storageUsage} status="active" strokeColor="#722ed1" />
                                        <div style={{ marginTop: '8px' }}>
                                            <Text type="secondary" style={{ fontSize: '12px' }}>{recentFiles.length} Recent ({totalFiles} total available)</Text>
                                        </div>
                                    </div>
                                </Card>
                            </Col>
                            <Col span={6}>
                                <Card
                                    size="small"
                                    className="file-stat-card file-stat-card--shared"
                                    style={{ background: '#f6ffed', border: 'none', borderRadius: '6px' }}
                                >
                                    <div style={{ textAlign: 'center' }}>
                                        <Text strong style={{ fontSize: '24px', color: '#52c41a' }}>86</Text>
                                        <div>
                                            <Text type="secondary" style={{ fontSize: '12px' }}>Shared Files</Text>
                                        </div>
                                    </div>
                                </Card>
                            </Col>
                        </Row>

                        {/* Uploaded Files List */}
                        <div style={{ marginBottom: 24 }}>
                            <Text strong style={{ fontSize: '14px', display: 'block', marginBottom: 12 }}>Uploaded Files</Text>
                            {uploadedFiles.length === 0 ? (
                                <div
                                    className="upload-placeholder"
                                    style={{
                                        border: '1px dashed #c7b1ff',
                                        borderRadius: 12,
                                        padding: '18px',
                                        background: '#ffffff'
                                    }}
                                >
                                    <Text type="secondary" style={{ fontSize: 12 }}>No manual uploads yet. Use the Upload Files button to add documents.</Text>
                                </div>
                            ) : (
                                <List
                                    dataSource={uploadedFiles}
                                    bordered
                                    renderItem={(file) => (
                                        <List.Item
                                            className="uploaded-file-item"
                                            actions={[
                                                <Button
                                                    key="remove"
                                                    size="small"
                                                    type="text"
                                                    danger
                                                    icon={<DeleteOutlined />}
                                                    onClick={() => handleRemoveUploadedFile(file.id)}
                                                >
                                                    Remove
                                                </Button>
                                            ]}
                                        >
                                            <List.Item.Meta
                                                avatar={
                                                    <div style={{
                                                        backgroundColor: '#f2f0ff',
                                                        borderRadius: 8,
                                                        padding: 8,
                                                        color: '#722ed1'
                                                    }}>
                                                        {file.icon}
                                                    </div>
                                                }
                                                title={
                                                    <Space direction="vertical" size={0}>
                                                        <Text strong>{file.name}</Text>
                                                        <Text type="secondary" style={{ fontSize: 12 }}>{file.type} • {file.size}</Text>
                                                    </Space>
                                                }
                                            />
                                            <Text type="secondary" style={{ fontSize: 12 }}>{file.time}</Text>
                                        </List.Item>
                                    )}
                                />
                            )}
                        </div>

                        {/* Recent Files Header */}
                        <div style={{ marginBottom: 16 }}>
                            <Text strong style={{ fontSize: '14px' }}>Recent Files</Text>
                        </div>

                        {/* Files Grid */}
                        <Row gutter={[16, 16]}>
                            {recentFiles.map((file, index) => (
                                <Col span={8} key={index}>
                                    <Card
                                        size="small"
                                        hoverable
                                        className="recent-file-card"
                                        style={{
                                            borderRadius: '6px',
                                            border: '1px solid #f0f0f0',
                                            height: '100%'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                                            <div style={{
                                                backgroundColor: '#f9f0ff',
                                                borderRadius: '6px',
                                                padding: '8px',
                                                marginRight: '12px',
                                                color: '#722ed1'
                                            }}>
                                                {file.icon}
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <Text strong style={{ fontSize: '12px', display: 'block' }}>
                                                    {file.name}
                                                </Text>
                                                <div style={{ marginTop: '4px' }}>
                                                    <Tag size="small" color="purple">{file.type}</Tag>
                                                    <Text type="secondary" style={{ fontSize: '10px', marginLeft: '8px' }}>
                                                        {file.size}
                                                    </Text>
                                                </div>
                                                <div style={{ marginTop: '8px' }}>
                                                    <Text type="secondary" style={{ fontSize: '10px' }}>
                                                        Updated {file.time}
                                                    </Text>
                                                </div>
                                            </div>
                                        </div>
                                    </Card>
                                </Col>
                            ))}
                        </Row>

                        {/* Quick Actions */}
                        <div className="quick-actions-panel" style={{ marginTop: 24, padding: '16px', background: '#fafafa', borderRadius: '6px' }}>
                            <Text strong style={{ fontSize: '14px', marginBottom: '12px', display: 'block' }}>
                                Quick Actions
                            </Text>
                            <Row gutter={[12, 12]}>
                                <Col>
                                    <Button className="quick-action-btn" icon={<FilePdfOutlined />} size="small">
                                        Export as PDF
                                    </Button>
                                </Col>
                                <Col>
                                    <Button className="quick-action-btn" icon={<FolderOutlined />} size="small">
                                        Create Folder
                                    </Button>
                                </Col>
                                <Col>
                                    <Button className="quick-action-btn" icon={<FileOutlined />} size="small">
                                        New Document
                                    </Button>
                                </Col>
                            </Row>
                        </div>
                    </Card>

                    {/* Extra content to show scrolling */}
                    <div style={{ height: '200px', marginTop: '24px' }} />
                </Content>

                {/* Fixed Right Sidebar - Calendar & Recent Activities */}
                <Sider
                    className="dashboard-sider dashboard-sider--right"
                    width={300}
                    theme="light"
                    style={{
                        position: 'fixed',
                        right: 0,
                        top: '64px',
                        height: 'calc(100vh - 64px)',
                        overflow: 'auto',
                        borderLeft: '1px solid #f0f0f0',
                        background: '#fff'
                    }}
                >
                    <div style={{ padding: '24px' }}>
                        {/* CALENDAR SECTION */}
                        <div style={{
                            background: '#fff',
                            borderRadius: 12,
                            padding: '16px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                            marginBottom: 24
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                                <Text strong style={{ fontSize: '16px' }}>{currentDate.format('MMMM YYYY')}</Text>
                                <Space>
                                    <Button
                                        size="small"
                                        type="text"
                                        icon={<LeftOutlined />}
                                        onClick={prevMonth}
                                        style={{ border: '1px solid #d9d9d9' }}
                                    />
                                    <Button
                                        size="small"
                                        type="text"
                                        icon={<RightOutlined />}
                                        onClick={nextMonth}
                                        style={{ border: '1px solid #d9d9d9' }}
                                    />
                                </Space>
                            </div>

                            {/* Calendar Grid */}
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', textAlign: 'center', gap: '4px' }}>
                                {/* Weekday headers */}
                                {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                                    <Text key={day} type="secondary" style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: 4 }}>{day}</Text>
                                ))}

                                {/* Empty days from previous month */}
                                {emptyDays.map(i => <div key={`empty-${i}`} style={{ height: '32px' }} />)}

                                {/* Days of current month */}
                                {daysArray.map(day => {
                                    const isToday = day === dayjs().date() && currentDate.isSame(dayjs(), 'month');
                                    return (
                                        <div
                                            key={day}
                                            className={`calendar-day${isToday ? ' calendar-day--today' : ''}`}
                                        >
                                            {day}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* RECENT ACTIVITIES SECTION */}
                        <div style={{ marginBottom: 24 }}>
                            <Title level={5} style={{ marginBottom: 12 }}>Recent activities</Title>
                            <div style={{
                                background: '#f5f5f5',
                                borderRadius: 12,
                                padding: '16px',
                                minHeight: 150
                            }}>
                                <List
                                    dataSource={recentActivities}
                                    renderItem={item => (
                                        <List.Item
                                            className="recent-activity-item"
                                        >
                                            <Typography.Text style={{ fontSize: '14px' }}>{item}</Typography.Text>
                                        </List.Item>
                                    )}
                                />
                            </div>
                            <div style={{ textAlign: 'right', marginTop: 8 }}>
                                <Text className="recent-activity-cta">
                                    see more
                                </Text>
                            </div>
                        </div>

                        {/* Optional: Additional widget */}
                        <div style={{
                            background: '#f9f0ff',
                            borderRadius: 12,
                            padding: '16px',
                            textAlign: 'center'
                        }}>
                            <Title level={5} style={{ color: '#722ed1' }}>Upcoming Events</Title>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                No events scheduled for today
                            </Text>
                        </div>
                    </div>
                </Sider>
            </Layout>



            <Modal
                title="Schedule Timeline Event"
                open={isEventModalOpen}
                onCancel={() => {
                    setEventModalOpen(false);
                    eventForm.resetFields();
                }}
                footer={null}
                width={520}
                destroyOnClose
                bodyStyle={{ paddingTop: 0 }}
            >
                <div style={{ marginBottom: 16 }}>
                    <Text type="secondary">Add milestones to keep the project timeline aligned.</Text>
                </div>
                <Form layout="vertical" form={eventForm} onFinish={handleEventSubmit}>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                label="Event Date"
                                name="date"
                                rules={[{ required: true, message: 'Please choose a date' }]}
                            >
                                <DatePicker style={{ width: '100%' }} size="large" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                label="Status"
                                name="status"
                                rules={[{ required: true, message: 'Select a status' }]}
                            >
                                <Select placeholder="Choose status" size="large">
                                    <Select.Option value="completed">Completed</Select.Option>
                                    <Select.Option value="in-progress">In Progress</Select.Option>
                                    <Select.Option value="pending">Pending</Select.Option>
                                </Select>
                            </Form.Item>
                        </Col>
                    </Row>
                    <Form.Item
                        label="Project"
                        name="project"
                        rules={[{ required: true, message: 'Please specify the project' }]}
                    >
                        <Input placeholder="e.g. Project Atlas" size="large" />
                    </Form.Item>
                    <Form.Item
                        label="Description"
                        name="description"
                        rules={[{ required: true, message: 'Please describe the event' }]}
                    >
                        <Input.TextArea rows={4} placeholder="What happens during this milestone?" />
                    </Form.Item>
                    <Button type="primary" htmlType="submit" block size="large">
                        Add Event
                    </Button>
                </Form>
            </Modal>
        </Layout>
    );
};

export default ProjectDashboard;