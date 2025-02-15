CREATE DATABASE mini;
USE mini;

-- ADMIN Table
CREATE TABLE ADMIN (
    UNIV_CODE CHAR(20) UNIQUE,
    CLG_ID CHAR(20) UNIQUE,
    ADMIN_ID CHAR(20) UNIQUE,
    PRIMARY KEY (UNIV_CODE, CLG_ID, ADMIN_ID)
);

-- COLLEGE Table
CREATE TABLE COLLEGE (
    UNIV_NAME VARCHAR(100),
    CLG_ID CHAR(20) PRIMARY KEY,
    CLG_NAME VARCHAR(100),
    UNIV_CODE CHAR(20),
    FOREIGN KEY (UNIV_CODE) REFERENCES ADMIN(UNIV_CODE) ON UPDATE CASCADE ON DELETE CASCADE
);

-- DEPARTMENT Table
CREATE TABLE DEPARTMENT (
    CLG_ID CHAR(20) ,
    DEPT_NAME VARCHAR(100) NOT NULL,
    DEPT_CODE VARCHAR(100),
    primary key(CLG_ID,DEPT_CODE),
    FOREIGN KEY (CLG_ID) REFERENCES COLLEGE(CLG_ID) ON UPDATE CASCADE ON DELETE CASCADE
);

-- FACULTY Table
CREATE TABLE FACULTY (
    PEN_NO VARCHAR(50) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    DEPT_CODE VARCHAR(100) NOT NULL,
    Designation VARCHAR(50),
    UNIV_CODE CHAR(20) NOT NULL,
    CLG_ID CHAR(20) NOT NULL,
    FOREIGN KEY (UNIV_CODE, CLG_ID) REFERENCES ADMIN(UNIV_CODE, CLG_ID) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (DEPT_CODE) REFERENCES DEPARTMENT(DEPT_CODE) ON UPDATE CASCADE ON DELETE CASCADE
);

-- STUDENT Table
CREATE TABLE STUDENT (
    UNIV_NO VARCHAR(50),
    Name VARCHAR(100) NOT NULL,
    Admission_NO VARCHAR(50) UNIQUE NOT NULL,
    DEPT_CODE VARCHAR(100) NOT NULL,
    Semester INT NOT NULL,  -- Changed to INT for easier comparison
    BATCH VARCHAR(50),
    UNIV_CODE CHAR(20) NOT NULL,
    CLG_ID CHAR(20) NOT NULL,
    PRIMARY KEY (UNIV_NO,UNIV_CODE),
    FOREIGN KEY (UNIV_CODE, CLG_ID) REFERENCES ADMIN(UNIV_CODE, CLG_ID) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (DEPT_CODE) REFERENCES DEPARTMENT(DEPT_CODE) ON UPDATE CASCADE ON DELETE CASCADE
);

-- BATCH Table (NEW)
CREATE TABLE BATCH (
    BATCH VARCHAR(50),
    DEPT_CODE VARCHAR(100) NOT NULL,
    ADVISOR_PEN_NO VARCHAR(50),
    FOREIGN KEY (DEPT_CODE) REFERENCES DEPARTMENT(DEPT_CODE) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (BATCH) REFERENCES STUDENT(BATCH) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (ADVISOR_PEN_NO) REFERENCES FACULTY(PEN_NO) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Courses (
    CourseCode VARCHAR(20),
    CourseTitle VARCHAR(200) NOT NULL,
    CourseType VARCHAR(50) NOT NULL,
    Semester INT NOT NULL,
    SCHEME VARCHAR(20) NOT NULL,
    DEPT_CODE VARCHAR(100),
    InstructorName VARCHAR(100),
    UNIV_CODE CHAR(20) NOT NULL,
    FOREIGN KEY (UNIV_CODE) REFERENCES ADMIN(UNIV_CODE),
    FOREIGN KEY (DEPT_CODE) REFERENCES DEPARTMENT(DEPT_CODE),
    PRIMARY KEY (CourseCode, InstructorName)
);

-- FACULTY_COURSE_MAPPING Table (NEW)
CREATE TABLE FACULTY_COURSE_MAPPING (
    FACULTY_PEN_NO VARCHAR(50),
    CourseCode VARCHAR(20),
    SEMESTER INT NOT NULL,
    advisor_pen_no varchar(50),
    PRIMARY KEY (FACULTY_PEN_NO, CourseCode, SEMESTER),
    FOREIGN KEY (FACULTY_PEN_NO) REFERENCES FACULTY(PEN_NO),
    FOREIGN KEY (ADVISOR_PEN_NO) REFERENCES FACULTY(PEN_NO),
    FOREIGN KEY (CourseCode) REFERENCES Courses(CourseCode)
);

-- STUDENT_COURSE_MAPPING Table (NEW)
CREATE TABLE STUDENT_COURSE_MAPPING (
    UNIV_NO VARCHAR(50),
    CourseCode VARCHAR(20),
    SEMESTER INT NOT NULL,
    PRIMARY KEY (UNIV_NO, CourseCode, SEMESTER),
    FOREIGN KEY (UNIV_NO) REFERENCES STUDENT(UNIV_NO),
    FOREIGN KEY (CourseCode) REFERENCES Courses(CourseCode)
);




CREATE TABLE CO (
    CO_NO INT NOT NULL,
    CO_DES VARCHAR(100) NOT NULL,
    CO_LEVEL VARCHAR(50) NOT NULL,
    CourseCode VARCHAR(20) NOT NULL,
    DEPT_CODE VARCHAR(100),
    is_approved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (DEPT_CODE) REFERENCES DEPARTMENT (DEPT_CODE),
    FOREIGN KEY (CourseCode) REFERENCES Courses (CourseCode),
    PRIMARY KEY (CO_NO, CourseCode)
);

INSERT INTO CO (CO_NO, CO_DES, CO_LEVEL, CourseCode, DEPT_CODE, is_approved)
VALUES
    (1, 'Understand basic programming concepts', 'Level 2', 'ME102', 'CS101', TRUE),
    (2, 'Apply programming concepts to solve problems', 'Level 3', 'CS101', 'CS101', TRUE),
    (3, 'Analyze algorithms for efficiency', 'Level 4', 'ME102', 'CS101', FALSE),
    (1, 'Understand database fundamentals', 'Level 2', 'CS102', 'CS101', TRUE);

CREATE TABLE PO (
    PO_NO INT PRIMARY KEY,
    PO_DES VARCHAR(100) NOT NULL,
    PO_LEVEL VARCHAR(50) NOT NULL
);

CREATE TABLE MARK (
    UNIV_NO VARCHAR(50),
    DEPT_CODE VARCHAR(100) NOT NULL,
    CourseCode VARCHAR(20),
    TOOL VARCHAR(50),
    MARK DECIMAL(3,2),
    Percentage DECIMAL(5,2),
    FOREIGN KEY (UNIV_NO) REFERENCES STUDENT (UNIV_NO),
    FOREIGN KEY (DEPT_CODE) REFERENCES DEPARTMENT (DEPT_CODE),
    FOREIGN KEY (CourseCode) REFERENCES Courses (CourseCode),
    PRIMARY KEY (UNIV_NO, CourseCode, TOOL)
);

CREATE TABLE CO_Attainment (
    CO_NO INT NOT NULL,
    CourseCode VARCHAR(20),
    TOOL VARCHAR(50),
    Threshold_Percentage DECIMAL(5,2),
    Attainment_Level INT,
    FOREIGN KEY (CO_NO, CourseCode) REFERENCES CO (CO_NO, CourseCode),
    PRIMARY KEY (CO_NO, CourseCode, TOOL)
);
CREATE TABLE Tool_Format (
    TOOL VARCHAR(50),
    Part_No INT,
    Question_No INT,
    Marks DECIMAL(5,2),
    CO_NO INT NOT NULL,
    CourseCode VARCHAR(20),
    FOREIGN KEY (CO_NO, CourseCode) REFERENCES CO (CO_NO, CourseCode),
    PRIMARY KEY (TOOL, Part_No, Question_No)
);


CREATE TABLE CO_Weightage (
    CO_NO INT NOT NULL,
    CourseCode VARCHAR(20),
    TOOL VARCHAR(50),
    Weightage_Percentage DECIMAL(5,2),
    FOREIGN KEY (CO_NO, CourseCode) REFERENCES CO (CO_NO, CourseCode),
    PRIMARY KEY (CO_NO, CourseCode, TOOL)
);
drop table co_weightage;

CREATE TABLE Indirect_Attainment (
    UNIV_NO VARCHAR(50),
    CourseCode VARCHAR(20),
    CO_NO INT NOT NULL,
    Survey_Score DECIMAL(5,2),
    FOREIGN KEY (UNIV_NO) REFERENCES Student (UNIV_NO),
    FOREIGN KEY (CourseCode, CO_NO) REFERENCES CO (CourseCode, CO_NO),
    PRIMARY KEY (UNIV_NO, CourseCode, CO_NO)
);

CREATE TABLE Attainment_Level (
    DEPT_CODE VARCHAR(100),
    Level INT NOT NULL,
    Min_Percentage DECIMAL(5,2),
    Max_Percentage DECIMAL(5,2),
    PRIMARY KEY (DEPT_CODE, Level),
    FOREIGN KEY (DEPT_CODE) REFERENCES Department (DEPT_CODE)
);

CREATE TABLE CO_Thresholds (
    DEPT_CODE VARCHAR(100),
    CourseCode VARCHAR(20),
    CO_NO INT,
    Threshold_Percentage DECIMAL(5,2),
    CoordinatorName VARCHAR(100),
    PRIMARY KEY (DEPT_CODE, CourseCode, CO_NO),
    FOREIGN KEY (DEPT_CODE) REFERENCES Department (DEPT_CODE),
    FOREIGN KEY (CourseCode, CO_NO) REFERENCES CO (CourseCode, CO_NO)
);
CREATE TABLE Attainment_Thresholds (
    DEPT_CODE VARCHAR(100),
    Direct_Threshold_Percentage DECIMAL(5,2),
    Indirect_Threshold_Percentage DECIMAL(5,2),
    PRIMARY KEY (DEPT_CODE),
    FOREIGN KEY (DEPT_CODE) REFERENCES Department (DEPT_CODE)
);

CREATE TABLE LOGIN (
    USER_NAME VARCHAR(100) unique,
    PEN_NO VARCHAR(100) ,
    PSW VARCHAR(20),
    UNIV_CODE CHAR(20),
    CLG_ID CHAR(20),
	ROLE_OF CHAR(10) CHECK (ROLE_OF IN ('ADMIN', 'FACULTY', 'HOD', 'MC', 'PRINCIPAL', 'ADVISOR')),
    primary key(pen_no,role_of,clg_id),
    FOREIGN KEY (PEN_NO) REFERENCES faculty (PEN_NO),
    FOREIGN KEY (UNIV_CODE, CLG_ID) REFERENCES ADMIN (UNIV_CODE, CLG_ID)
);

CREATE TABLE ROLES (
    PEN_NO VARCHAR(100),
    UNIV_CODE CHAR(20),
    CLG_ID CHAR(20),
    ROLE_OF CHAR(10) CHECK (ROLE_OF IN ('ADMIN', 'FACULTY', 'HOD', 'MC', 'PRINCIPAL', 'ADVISOR')),
    PRIMARY KEY (PEN_NO, ROLE_OF, UNIV_CODE, CLG_ID),
    FOREIGN KEY (PEN_NO) REFERENCES faculty (PEN_NO),
    FOREIGN KEY (UNIV_CODE, CLG_ID) REFERENCES ADMIN (UNIV_CODE, CLG_ID)
);
-- TRIGGER: Auto Remove Faculty-Course Mapping When Students Upgrade
DELIMITER //
CREATE TRIGGER update_faculty_assignment
BEFORE UPDATE ON STUDENT
FOR EACH ROW
BEGIN
    IF NEW.Semester > OLD.Semester THEN
        DELETE FROM FACULTY_COURSE_MAPPING 
        WHERE SEMESTER = OLD.Semester;
    END IF;
END;
//
DELIMITER ;




INSERT INTO ADMIN (UNIV_NAME, UNIV_CODE, CLG_ID, ADMIN_ID) VALUES
('University A', 'UNIV001', 'CLG001', 'ADMIN001'),
('University B', 'UNIV002', 'CLG002', 'ADMIN002'),
('University C', 'UNIV003', 'CLG003', 'ADMIN003');

-- Inserting data into COLLEGE table
INSERT INTO COLLEGE (CLG_ID, CLG_NAME, UNIV_CODE) VALUES
('CLG001', 'College of Science', 'UNIV001'),
('CLG002', 'College of Arts', 'UNIV002'),
('CLG003', 'College of Engineering', 'UNIV003');

-- Inserting data into DEPARTMENT table
INSERT INTO DEPARTMENT (DEPT_NAME, DEPT_CODE) VALUES
('Computer Science', 'CS101'),
('Mechanical Engineering', 'ME102'),
('Electrical Engineering', 'EE103'),
('Mathematics', 'MATH104'),
('Physics', 'PHYS105');

-- Inserting data into FACULTY table
INSERT INTO FACULTY (PEN_NO, Name, DEPT_CODE, Email, PhoneNumber, Designation, Qualification, DateOfJoining, UNIV_CODE, CLG_ID) VALUES
('PEN001', 'Alice Smith', 'CS101', 'alice.smith@univ1.edu', '1234567890', 'Professor', 'PhD in Computer Science', '2015-08-01', 'UNIV001', 'CLG001'),
('PEN002', 'Bob Johnson', 'ME102', 'bob.johnson@univ2.edu', '2345678901', 'Associate Professor', 'MSc in Mechanical Engineering', '2016-09-01', 'UNIV002', 'CLG002'),
('PEN003', 'Charlie Brown', 'EE103', 'charlie.brown@univ3.edu', '3456789012', 'Assistant Professor', 'MTech in Electrical Engineering', '2017-10-01', 'UNIV003', 'CLG003'),
('PEN004', 'Diana Prince', 'MATH104', 'diana.prince@univ1.edu', '4567890123', 'Lecturer', 'MSc in Mathematics', '2018-11-01', 'UNIV001', 'CLG001'),
('PEN005', 'Ethan Hunt', 'PHYS105', 'ethan.hunt@univ2.edu', '5678901234', 'Professor', 'PhD in Physics', '2019-12-01', 'UNIV002', 'CLG002');

-- Inserting data into STUDENT table
INSERT INTO STUDENT (UNIV_NO, Name, AdmissionNumber, DEPT_CODE, Semester, Email, PhoneNumber, GuardianName, DateOfBirth, UNIV_CODE, CLG_ID) VALUES
('UNIV001001', 'John Doe', 'AD001', 'CS101', 1, 'john.doe@univ1.edu', '6789012345', 'Jane Doe', '2000-01-01', 'UNIV001', 'CLG001'),
('UNIV001002', 'Mary Jane', 'AD002', 'CS101', 2, 'mary.jane@univ1.edu', '7890123456', 'Peter Jane', '2000-02-01', 'UNIV001', 'CLG001'),
('UNIV002001', 'Tom Hardy', 'AD003', 'ME102', 1, 'tom.hardy@univ2.edu', '8901234567', 'Sarah Hardy', '2000-03-01', 'UNIV002', 'CLG002'),
('UNIV002002', 'Emma Watson', 'AD004', 'ME102', 2, 'emma.watson@univ2.edu', '9012345678', 'Daniel Watson', '2000-04-01', 'UNIV002', 'CLG002'),
('UNIV003001', 'Chris Evans', 'AD005', 'EE103', 1, 'chris.evans@univ3.edu', '0123456789', 'Linda Evans', '2000-05-01', 'UNIV003', 'CLG003');


INSERT INTO BATCH (DEPT_CODE, SEMESTER, ADVISOR_PEN_NO) VALUES
('CS101', 1, 'PEN001'),
('CS101', 2, 'PEN001'),
('ME102', 1, 'PEN002'),
('ME102', 2, 'PEN002'),
('EE103', 1, 'PEN003');

-- Inserting data into Courses table
INSERT INTO Courses (CourseCode, CourseTitle, CourseType, CreditHours, Semester, SCHEME, DEPT_CODE, InstructorName, UNIV_CODE) VALUES
('CS101', 'Introduction to Computer Science', 'Core', 3, 1, '2023', 'CS101', 'Alice Smith', 'UNIV001'),
('CS102', 'Data Structures', 'Core', 3, 2, '2023', 'CS101', 'Alice Smith', 'UNIV001'),
('ME101', 'Thermodynamics', 'Core', 3, 1, '2023', 'ME102', 'Bob Johnson', 'UNIV002'),
('ME102', 'Fluid Mechanics', 'Core', 3, 2, '2023', 'ME102', 'Bob Johnson', 'UNIV002'),
('EE101', 'Circuit Analysis', 'Core', 3, 1, '2023', 'EE103', 'Charlie Brown', 'UNIV003');

-- Inserting data into FACULTY_COURSE_MAPPING table
INSERT INTO FACULTY_COURSE_MAPPING (FACULTY_PEN_NO, CourseCode, SEMESTER) VALUES
('PEN001', 'CS101', 1),
('PEN001', 'CS102', 2),
('PEN002', 'ME101', 1),
('PEN002', 'ME102', 2),
('PEN003', 'EE101', 1);

-- Inserting data into STUDENT_COURSE_MAPPING table
INSERT INTO STUDENT_COURSE_MAPPING (UNIV_NO, CourseCode, SEMESTER) VALUES
('UNIV001001', 'CS101', 1),
('UNIV001002', 'CS102', 2),
('UNIV002001', 'ME101', 1),
('UNIV002002', 'ME102', 2),
('UNIV003001', 'EE101', 1);

INSERT INTO ROLES (UNIV_CODE, CLG_ID, PEN_NO, ROLE_OF) VALUES 
('UNIV001', 'CLG001', 'PEN001', 'FACULTY'),
('UNIV001', 'CLG001', 'PEN004', 'ADVISOR'),
('UNIV002', 'CLG002', 'PEN002', 'FACULTY'),
('UNIV002', 'CLG002', 'PEN005', 'ADVISOR'),
('UNIV002', 'CLG002', 'PEN002', 'ADVISOR'),
('UNIV003', 'CLG003', 'PEN003', 'FACULTY');

INSERT INTO LOGIN (USER_NAME, PEN_NO, PSW, ROLE_OF, UNIV_CODE, CLG_ID) VALUES
('alice.smith', 'PEN001', 'password123', 'FACULTY', 'UNIV001', 'CLG001'),
('bob.johnson', 'PEN002', 'password123', 'FACULTY', 'UNIV002', 'CLG002'),
('charlie.brown', 'PEN003', 'password123', 'FACULTY', 'UNIV003', 'CLG003'),
('diana.prince', 'PEN004', 'password123', 'ADVISOR', 'UNIV001', 'CLG001'),
('ethan.hunt', 'PEN005', 'password123', 'ADVISOR', 'UNIV002', 'CLG002');

