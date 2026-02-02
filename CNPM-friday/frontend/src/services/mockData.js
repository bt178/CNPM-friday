// Mock Data for Admin Dashboard
export const mockSubjects = [
    { subject_id: 1, subject_code: 'INT1001', subject_name: 'Introduction to Programming', dept_id: 1, credits: 3 },
    { subject_id: 2, subject_code: 'INT1002', subject_name: 'Data Structures & Algorithms', dept_id: 1, credits: 4 },
    { subject_id: 3, subject_code: 'INT1003', subject_name: 'Database Systems', dept_id: 1, credits: 3 },
    { subject_id: 4, subject_code: 'INT1004', subject_name: 'Computer Networks', dept_id: 1, credits: 3 },
    { subject_id: 5, subject_code: 'INT1005', subject_name: 'Operating Systems', dept_id: 1, credits: 3 },
    { subject_id: 6, subject_code: 'ECO1001', subject_name: 'Microeconomics', dept_id: 2, credits: 3 },
    { subject_id: 7, subject_code: 'ECO1002', subject_name: 'Macroeconomics', dept_id: 2, credits: 3 },
];

export const mockClasses = [
    { class_id: 1, class_code: 'SE101_2024_1', subject_name: 'Introduction to Programming', lecturer_name: 'Nguyen Van A', semester_id: 20241 },
    { class_id: 2, class_code: 'SE102_2024_1', subject_name: 'Data Structures', lecturer_name: 'Tran Thi B', semester_id: 20241 },
    { class_id: 3, class_code: 'SE103_2024_1', subject_name: 'Database Systems', lecturer_name: 'Le Van C', semester_id: 20241 },
    { class_id: 4, class_code: 'NET101_2024_1', subject_name: 'Computer Networks', lecturer_name: 'Pham Thi D', semester_id: 20241 },
    { class_id: 5, class_code: 'OS101_2024_1', subject_name: 'Operating Systems', lecturer_name: 'Hoang Van E', semester_id: 20241 },
];

export const mockUsers = [
    { user_id: 'u1', email: 'admin@uth.edu.vn', full_name: 'Admin User', role_name: 'ADMIN', is_active: true },
    { user_id: 'u2', email: 'nguyenvana@uth.edu.vn', full_name: 'Nguyễn Văn A', role_name: 'LECTURER', is_active: true },
    { user_id: 'u3', email: 'tranthib@uth.edu.vn', full_name: 'Trần Thị B', role_name: 'LECTURER', is_active: true },
    { user_id: 'u4', email: 'student1@uth.edu.vn', full_name: 'Lê Học Sinh', role_name: 'STUDENT', is_active: true },
    { user_id: 'u5', email: 'student2@uth.edu.vn', full_name: 'Phạm Sinh Viên', role_name: 'STUDENT', is_active: true },
];

export const mockProjects = [
    { key: '1', proposer: 'Dr. John', topic: 'Smart Inventory System', category: 'IoT', date: 'Nov 15 2025', status: 'Pending' },
    { key: '2', proposer: 'Dr. John', topic: 'Smart Inventory System', category: 'IoT', date: 'Nov 15 2025', status: 'Pending' },
    { key: '3', proposer: 'Dr. John', topic: 'Smart Inventory System', category: 'IoT', date: 'Nov 15 2025', status: 'Pending' },
    { key: '4', proposer: 'Dr. Smith', topic: 'AI Health Monitor', category: 'AI', date: 'Dec 01 2025', status: 'Pending' },
    { key: '5', proposer: 'Dr. Brown', topic: 'Blockchain Voting', category: 'Blockchain', date: 'Dec 05 2025', status: 'Pending' },
    { key: '6', proposer: 'Dr. John', topic: 'Smart Campus App', category: 'Mobile', date: 'Nov 20 2025', status: 'Pending' },
    { key: '7', proposer: 'Dr. Smith', topic: 'Library Management', category: 'Web', date: 'Nov 25 2025', status: 'Pending' },
    { key: '8', proposer: 'Dr. Brown', topic: 'Drone Delivery', category: 'IoT', date: 'Dec 10 2025', status: 'Pending' },
];
