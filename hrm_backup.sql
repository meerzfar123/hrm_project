--
-- PostgreSQL database dump
--

\restrict 6uCod2mrrF9f495JhFhe8h7Qa82cRPQ1Z08AcEa2Kw5uPMo0AaFAzrek2HuJmTG

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: apply_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.apply_attempts (
    attempt_id integer NOT NULL,
    ip_address character varying(64) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.apply_attempts OWNER TO postgres;

--
-- Name: apply_attempts_attempt_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.apply_attempts_attempt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.apply_attempts_attempt_id_seq OWNER TO postgres;

--
-- Name: apply_attempts_attempt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.apply_attempts_attempt_id_seq OWNED BY public.apply_attempts.attempt_id;


--
-- Name: candidate_answers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidate_answers (
    answer_id integer NOT NULL,
    candidate_id integer NOT NULL,
    question_id integer NOT NULL,
    answer_text text
);


ALTER TABLE public.candidate_answers OWNER TO postgres;

--
-- Name: candidate_answers_answer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.candidate_answers_answer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_answers_answer_id_seq OWNER TO postgres;

--
-- Name: candidate_answers_answer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.candidate_answers_answer_id_seq OWNED BY public.candidate_answers.answer_id;


--
-- Name: candidate_queries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidate_queries (
    query_id integer NOT NULL,
    candidate_id integer NOT NULL,
    question text NOT NULL,
    reply text,
    asked_at timestamp without time zone DEFAULT now() NOT NULL,
    replied_at timestamp without time zone
);


ALTER TABLE public.candidate_queries OWNER TO postgres;

--
-- Name: candidate_queries_query_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.candidate_queries_query_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_queries_query_id_seq OWNER TO postgres;

--
-- Name: candidate_queries_query_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.candidate_queries_query_id_seq OWNED BY public.candidate_queries.query_id;


--
-- Name: candidate_rankings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidate_rankings (
    ranking_id integer NOT NULL,
    candidate_id integer NOT NULL,
    job_id integer NOT NULL,
    rank_position integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.candidate_rankings OWNER TO postgres;

--
-- Name: candidate_rankings_ranking_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.candidate_rankings_ranking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_rankings_ranking_id_seq OWNER TO postgres;

--
-- Name: candidate_rankings_ranking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.candidate_rankings_ranking_id_seq OWNED BY public.candidate_rankings.ranking_id;


--
-- Name: candidates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidates (
    candidate_id integer NOT NULL,
    user_id integer,
    job_id integer,
    name text NOT NULL,
    email text,
    cv_text text,
    cv_file_path text,
    experience_years integer,
    education text,
    expected_salary integer,
    score integer,
    screening_result text,
    status text DEFAULT 'applied'::text NOT NULL,
    phone character varying(50) DEFAULT ''::character varying,
    offer_salary numeric(12,2),
    joining_date date,
    candidate_source text
);


ALTER TABLE public.candidates OWNER TO postgres;

--
-- Name: candidates_candidate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.candidates_candidate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidates_candidate_id_seq OWNER TO postgres;

--
-- Name: candidates_candidate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.candidates_candidate_id_seq OWNED BY public.candidates.candidate_id;


--
-- Name: company_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_info (
    info_id integer NOT NULL,
    company_name text,
    about_us text,
    mission text,
    address text,
    website text,
    contact_email text,
    updated_by integer,
    tagline character varying(200) DEFAULT ''::character varying,
    vision text DEFAULT ''::text,
    services text DEFAULT ''::text,
    team text DEFAULT ''::text,
    phone character varying(50) DEFAULT ''::character varying,
    facebook character varying(200) DEFAULT ''::character varying,
    linkedin character varying(200) DEFAULT ''::character varying,
    instagram character varying(200) DEFAULT ''::character varying,
    twitter character varying(200) DEFAULT ''::character varying
);


ALTER TABLE public.company_info OWNER TO postgres;

--
-- Name: company_info_info_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_info_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_info_info_id_seq OWNER TO postgres;

--
-- Name: company_info_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_info_info_id_seq OWNED BY public.company_info.info_id;


--
-- Name: email_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_codes (
    code_id integer NOT NULL,
    email text NOT NULL,
    code_hash text NOT NULL,
    purpose text DEFAULT 'signup'::text NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    wrong_tries integer DEFAULT 0 NOT NULL,
    used boolean DEFAULT false NOT NULL
);


ALTER TABLE public.email_codes OWNER TO postgres;

--
-- Name: email_codes_code_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.email_codes_code_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.email_codes_code_id_seq OWNER TO postgres;

--
-- Name: email_codes_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.email_codes_code_id_seq OWNED BY public.email_codes.code_id;


--
-- Name: interviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interviews (
    interview_id integer NOT NULL,
    candidate_id integer,
    interview_date timestamp without time zone,
    feedback text,
    rating integer,
    instructions text
);


ALTER TABLE public.interviews OWNER TO postgres;

--
-- Name: interviews_interview_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interviews_interview_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interviews_interview_id_seq OWNER TO postgres;

--
-- Name: interviews_interview_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interviews_interview_id_seq OWNED BY public.interviews.interview_id;


--
-- Name: job_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_questions (
    question_id integer NOT NULL,
    job_id integer NOT NULL,
    question_text text NOT NULL
);


ALTER TABLE public.job_questions OWNER TO postgres;

--
-- Name: job_questions_question_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.job_questions_question_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.job_questions_question_id_seq OWNER TO postgres;

--
-- Name: job_questions_question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.job_questions_question_id_seq OWNED BY public.job_questions.question_id;


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jobs (
    job_id integer NOT NULL,
    title text NOT NULL,
    department text,
    salary_range text,
    location text,
    description text,
    requirements text,
    benefits text,
    deadline date,
    poster_path text,
    created_by integer,
    status text DEFAULT 'draft'::text NOT NULL,
    reject_reason text,
    approved_by integer,
    CONSTRAINT jobs_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'pending_approval'::text, 'rejected'::text, 'published'::text, 'closed'::text])))
);


ALTER TABLE public.jobs OWNER TO postgres;

--
-- Name: jobs_job_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.jobs_job_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jobs_job_id_seq OWNER TO postgres;

--
-- Name: jobs_job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.jobs_job_id_seq OWNED BY public.jobs.job_id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    notification_id integer NOT NULL,
    to_role text,
    to_user_id integer,
    message text NOT NULL,
    job_id integer,
    is_read boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_notification_id_seq OWNER TO postgres;

--
-- Name: notifications_notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_notification_id_seq OWNED BY public.notifications.notification_id;


--
-- Name: offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.offers (
    offer_id integer NOT NULL,
    candidate_id integer,
    offer_status text DEFAULT 'pending'::text NOT NULL,
    offered_salary numeric,
    joining_date date,
    offer_token text,
    sent_at timestamp without time zone,
    responded_at timestamp without time zone,
    CONSTRAINT offers_offer_status_check CHECK ((offer_status = ANY (ARRAY['pending'::text, 'accepted'::text, 'rejected'::text])))
);


ALTER TABLE public.offers OWNER TO postgres;

--
-- Name: offers_offer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.offers_offer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.offers_offer_id_seq OWNER TO postgres;

--
-- Name: offers_offer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.offers_offer_id_seq OWNED BY public.offers.offer_id;


--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_resets (
    reset_id integer NOT NULL,
    email character varying(255) NOT NULL,
    code_hash text NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    used boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.password_resets OWNER TO postgres;

--
-- Name: password_resets_reset_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.password_resets_reset_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.password_resets_reset_id_seq OWNER TO postgres;

--
-- Name: password_resets_reset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.password_resets_reset_id_seq OWNED BY public.password_resets.reset_id;


--
-- Name: role_invites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_invites (
    invite_id integer NOT NULL,
    email text NOT NULL,
    role text DEFAULT 'manager'::text NOT NULL,
    invited_by integer,
    status text DEFAULT 'pending'::text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT role_invites_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'accepted'::text, 'removed'::text])))
);


ALTER TABLE public.role_invites OWNER TO postgres;

--
-- Name: role_invites_invite_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.role_invites_invite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.role_invites_invite_id_seq OWNER TO postgres;

--
-- Name: role_invites_invite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.role_invites_invite_id_seq OWNED BY public.role_invites.invite_id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    token text NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL,
    salt text NOT NULL,
    role text DEFAULT 'candidate'::text NOT NULL,
    email_verified boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT users_role_check CHECK ((role = ANY (ARRAY['candidate'::text, 'hr'::text, 'manager'::text])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: apply_attempts attempt_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apply_attempts ALTER COLUMN attempt_id SET DEFAULT nextval('public.apply_attempts_attempt_id_seq'::regclass);


--
-- Name: candidate_answers answer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_answers ALTER COLUMN answer_id SET DEFAULT nextval('public.candidate_answers_answer_id_seq'::regclass);


--
-- Name: candidate_queries query_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_queries ALTER COLUMN query_id SET DEFAULT nextval('public.candidate_queries_query_id_seq'::regclass);


--
-- Name: candidate_rankings ranking_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_rankings ALTER COLUMN ranking_id SET DEFAULT nextval('public.candidate_rankings_ranking_id_seq'::regclass);


--
-- Name: candidates candidate_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidates ALTER COLUMN candidate_id SET DEFAULT nextval('public.candidates_candidate_id_seq'::regclass);


--
-- Name: company_info info_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_info ALTER COLUMN info_id SET DEFAULT nextval('public.company_info_info_id_seq'::regclass);


--
-- Name: email_codes code_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_codes ALTER COLUMN code_id SET DEFAULT nextval('public.email_codes_code_id_seq'::regclass);


--
-- Name: interviews interview_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews ALTER COLUMN interview_id SET DEFAULT nextval('public.interviews_interview_id_seq'::regclass);


--
-- Name: job_questions question_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_questions ALTER COLUMN question_id SET DEFAULT nextval('public.job_questions_question_id_seq'::regclass);


--
-- Name: jobs job_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs ALTER COLUMN job_id SET DEFAULT nextval('public.jobs_job_id_seq'::regclass);


--
-- Name: notifications notification_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN notification_id SET DEFAULT nextval('public.notifications_notification_id_seq'::regclass);


--
-- Name: offers offer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.offers ALTER COLUMN offer_id SET DEFAULT nextval('public.offers_offer_id_seq'::regclass);


--
-- Name: password_resets reset_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets ALTER COLUMN reset_id SET DEFAULT nextval('public.password_resets_reset_id_seq'::regclass);


--
-- Name: role_invites invite_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_invites ALTER COLUMN invite_id SET DEFAULT nextval('public.role_invites_invite_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: apply_attempts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.apply_attempts (attempt_id, ip_address, created_at) FROM stdin;
30	127.0.0.1	2026-11-22 12:29:16.962426
31	127.0.0.1	2026-11-22 12:29:43.560544
32	127.0.0.1	2026-11-22 12:37:19.92535
33	127.0.0.1	2026-11-22 12:38:11.740007
34	127.0.0.1	2026-11-22 12:39:50.1391
35	127.0.0.1	2026-11-22 12:40:16.820022
36	127.0.0.1	2026-11-22 12:44:11.206921
37	127.0.0.1	2026-11-22 12:44:53.541434
38	127.0.0.1	2026-11-22 12:47:53.047838
39	127.0.0.1	2026-11-22 12:48:11.369951
\.


--
-- Data for Name: candidate_answers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.candidate_answers (answer_id, candidate_id, question_id, answer_text) FROM stdin;
1	1	7	fresher
2	1	8	zafarullah
3	2	7	01
4	2	8	saddam
5	3	11	00
6	3	12	no
7	3	13	no
8	3	14	88
9	3	15	today
10	5	16	qq
11	5	17	ss
12	5	18	xcvdcv
13	5	19	ssss
14	5	20	ss
15	6	16	1
16	6	17	11
17	6	18	aa
18	6	19	a
19	6	20	aa
20	7	16	00
21	7	17	jhg
22	7	18	hjg
23	7	19	888
24	7	20	000
25	8	16	ewe
26	8	17	ewe
27	8	18	dsaad
28	8	19	22
29	8	20	2222
30	18	21	shahid
31	18	22	4510456091703
32	18	23	12
33	19	21	zidais
34	19	22	465347231456237
35	19	23	9 year
36	21	21	ali hyder
37	21	22	4510456091703
38	21	23	10y
39	22	21	zaki mr
40	22	22	4510456091703
41	22	23	10y
42	23	28	zafar
43	23	29	4510456091703
44	23	30	4 year
45	23	31	communication skill
46	24	32	kami
47	24	33	4510456091703
48	24	34	bs sociology
49	25	35	no
50	26	35	88
51	27	35	9
52	28	35	nj
53	29	35	yes
54	30	35	no
55	31	37	no
56	32	37	yes
57	33	37	no
58	34	37	no
59	35	35	no
60	36	32	shahid
61	36	33	4510456091703
62	36	34	bs sociology
63	37	28	adil khan
64	37	29	4250130900
65	37	30	3
66	37	31	teaching
67	38	37	no
68	39	37	no
69	40	21	sad
70	40	22	6757
71	40	23	no
72	41	16	no
73	41	17	no
74	41	18	no
75	41	19	no
76	41	20	no
\.


--
-- Data for Name: candidate_queries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.candidate_queries (query_id, candidate_id, question, reply, asked_at, replied_at) FROM stdin;
1	4	locations	\N	2026-11-01 23:24:47.955941	\N
\.


--
-- Data for Name: candidate_rankings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.candidate_rankings (ranking_id, candidate_id, job_id, rank_position, created_at) FROM stdin;
86	33	22	1	2026-11-22 13:06:40.160881
87	34	22	2	2026-11-22 13:06:40.209256
88	38	22	3	2026-11-22 13:06:40.257061
95	40	18	1	2026-11-22 13:14:09.55128
\.


--
-- Data for Name: candidates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.candidates (candidate_id, user_id, job_id, name, email, cv_text, cv_file_path, experience_years, education, expected_salary, score, screening_result, status, phone, offer_salary, joining_date, candidate_source) FROM stdin;
3	9	15	sudheer	sudheer@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends,\ncommunities and research methods, together with strong record-keeping, documentation and MS Office\nskills, is needed to collect, organize and maintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nHRM Intern (Remote), xLoop Digital — Sep 2026 – Present\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  AI Agentic Training Program, xLoop Digital — Apr – Aug 2026\n Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul –\nDec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management;\ncommunication and team coordination\n Technology: AI agentic tools and basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	49aedec54bbf44468b4b2b1033376eb9.pdf	0	Bs. sociology	30000	8	Weak match. Matching words: tasks	selected		\N	\N	\N
1	7	14	haseeb	hhaseebzafar3@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends, communities and\nresearch methods, together with strong record-keeping, documentation and MS Office skills, is needed to collect, organize and\nmaintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on schedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul – Dec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management; communication and team\ncoordination\n Technology: Basic IT (C.I.T)\nREFERENCES\nAvailable on request.\n	639ac45adda5479faa4ae91bbf42db16.pdf	0	Bs. sociology	30000	9	Weak match. Matching words: tasks	shortlisted		\N	\N	\N
2	8	14	saddam	sadammahar500@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	93b732c8399f4866b8cbb382c5b21520.pdf	0	bs sociology	40000	9	Weak match. Matching words: tasks	offer_pending		80000.00	2026-12-01	\N
4	10	9	zahid	haseebzafar3@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends, communities and\nresearch methods, together with strong record-keeping, documentation and MS Office skills, is needed to collect, organize and\nmaintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on schedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul – Dec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management; communication and team\ncoordination\n Technology: Basic IT (C.I.T)\nREFERENCES\nAvailable on request.\n	69685657b6d342de931cc299fdd03ffb.pdf	0	Bs. sociology	30000	0	Weak match. Matching words: none	shortlisted		\N	\N	\N
5	8	17	saddam	sadammahar500@gmail.com	Zafarullah\nKarachi, Pakistan  |  meer34499@gmail.com  |  +92 307 3674508\nCOVER LETTER\nRe: AI Research Engineer (Agentic Post-training) — 100% Remote Worldwide\nDear Tether Hiring Team,\nI am writing to express my interest in the AI Research Engineer (Agentic Post-training) position at\nTether. I recently completed the AI Agentic Training Program at xLoop Digital and have developed\nknowledge of AI automation tools and concepts, including Make.com, n8n, Microsoft Azure, and\nRetrieval-Augmented Generation (RAG) models. I am eager to build on this foundation and contribute\nto the development and evaluation of intelligent AI agent systems.\nMy learning in workflow automation with Make.com and n8n has introduced me to ways of connecting\ntools and organizing multi-step processes. My knowledge of Microsoft Azure and RAG concepts has\nalso encouraged me to explore how cloud-based AI services and retrieval-grounded systems can\nsupport useful, context-aware applications. I am motivated to deepen my practical skills in agent\nworkflows, tool use, model evaluation, and post-training methods.\nIn addition to my AI training, I am completing a B.Sc. in Sociology at the University of Karachi and\nbring experience in remote HR support, teaching, documentation, and team coordination. These\nresponsibilities have helped me develop analytical thinking, clear communication, attention to detail,\nand the ability to organize work and meet deadlines. I would bring this same discipline, curiosity, and\nwillingness to learn to a collaborative technical team.\nI understand that agentic post-training is a specialized area, and I am keen to continue developing\nthe technical depth needed to contribute effectively. I would welcome the opportunity to discuss how\nmy AI automation training, knowledge of RAG and cloud AI concepts, and transferable professional\nskills could support Tether's work.\nThank you for your time and consideration. I look forward to the possibility of discussing my\napplication with you.\nSincerely,\nZafarullah\nKarachi, Pakistan\n	8ac7f938e9334c24b3437eeca9c49be9.pdf	0	00	0	0	Weak match. Matching words: none	applied		\N	\N	\N
7	\N	17	zafar123	sajid123@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends,\ncommunities and research methods, together with strong record-keeping, documentation and MS Office\nskills, is needed to collect, organize and maintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nHRM Intern (Remote), xLoop Digital — Sep 2026 – Present\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  AI Agentic Training Program, xLoop Digital — Apr – Aug 2026\n Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul –\nDec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management;\ncommunication and team coordination\n Technology: AI agentic tools and basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	4a85d079cfd145b99a65b0b4316d7219.pdf	0	Bs. sociology	30000	9	Weak match. Matching words: tasks	applied	03073674508	\N	\N	\N
8	\N	17	sabir	shakeel123@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends,\ncommunities and research methods, together with strong record-keeping, documentation and MS Office\nskills, is needed to collect, organize and maintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nHRM Intern (Remote), xLoop Digital — Sep 2026 – Present\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  AI Agentic Training Program, xLoop Digital — Apr – Aug 2026\n Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul –\nDec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management;\ncommunication and team coordination\n Technology: AI agentic tools and basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	632fd79cacf84c69a455f66f99ae28e4.pdf	10	Bs. sociology and computer	8888888	29	Weak match. Matching words: tasks	selected	03073674508	\N	\N	\N
10	\N	6	zafar ullah	meer34499@gmail.com			0		0	0	Manual HR candidate - CV not provided.	applied	03073674508	\N	\N	LinkedIn
6	\N	17	Zafar Ullah	meer34499@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	ebd9db07b0d74e0db2ea3ed2ef53a191.pdf	0	bs sociology	40000	9	Weak match. Matching words: tasks	selected	03073674508	\N	\N	\N
9	\N	1	asad	asad123@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends,\ncommunities and research methods, together with strong record-keeping, documentation and MS Office\nskills, is needed to collect, organize and maintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nHRM Intern (Remote), xLoop Digital — Sep 2026 – Present\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  AI Agentic Training Program, xLoop Digital — Apr – Aug 2026\n Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul –\nDec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management;\ncommunication and team coordination\n Technology: AI agentic tools and basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	79f05070c6f94e118cbe6e599040bc97.pdf	3	Bs. sociology	30000	12	Weak match. Matching words: none	selected	03073674508	\N	\N	\N
14	\N	7	gamu				0		0	0	Manual HR candidate - CV not provided.	applied		\N	\N	
15	\N	3	zaman				0		0	0	Manual HR candidate - CV not provided.	applied		\N	\N	
11	\N	13	saad				0		0	0	Manual HR candidate - CV not provided.	shortlisted		\N	\N	
18	\N	18	kaleem	asad123@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends,\ncommunities and research methods, together with strong record-keeping, documentation and MS Office\nskills, is needed to collect, organize and maintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nHRM Intern (Remote), xLoop Digital — Sep 2026 – Present\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  AI Agentic Training Program, xLoop Digital — Apr – Aug 2026\n Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul –\nDec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management;\ncommunication and team coordination\n Technology: AI agentic tools and basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	76e32ec9457c47cea1a06e8725589c9d.pdf	3	Bs. sociology	30000	30	Weak match. Matching words: tasks, teacher	rejected	03073674508	\N	\N	\N
16	\N	7	qari	ahad123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	f2bd263346f24405a2d7cb61733894ef.pdf	0		0	10	Weak match. Matching words: tasks	shortlisted	03012345678	\N	\N	Recruitment Website
17	\N	15	saqi	ahad123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	fbbb145f39334b17bdc0037853fe8923.pdf	0		0	8	Weak match. Matching words: tasks	selected	03012345678	\N	\N	LinkedIn
19	\N	18	zahid	asad321@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	5bbe9f6df94f4a50890ce6499c4154d1.pdf	3	Bs. sociology	30000	30	Weak match. Matching words: tasks, teacher	offer_pending	03073674508	30000.00	2026-11-16	\N
20	\N	18	badshaH	BAD@gmail.com			0		0	0	Manual HR candidate - CV not provided.	hired		3000.00	2026-11-26	
21	\N	18	hyder	meer34492@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	e42e264fbbe14285b86d2208b1c80ffa.pdf	23	Bs. sociology and computer	8000	38	Weak match. Matching words: tasks, teacher	offer_rejected	03073674508	200000.00	2026-11-30	\N
23	\N	19	zafar ullah	zafar23344@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	178ac27aa0da41fb813eec6b641f63cc.pdf	3	Bs. sociology	30000	58	Partial Fit. Exact skills: communication. Missing skills: teamwork.	applied	03073674508	\N	\N	\N
22	\N	18	zaki	zaki34499@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends, communities and\nresearch methods, together with strong record-keeping, documentation and MS Office skills, is needed to collect, organize and\nmaintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on schedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul – Dec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management; communication and team\ncoordination\n Technology: Basic IT (C.I.T)\nREFERENCES\nAvailable on request.\n	3ba89fbe3004411281dff7be3a0d81de.pdf	10	Bs. sociology	8888888	38	Weak match. Matching words: tasks, teacher	selected	03073674508	\N	\N	\N
25	\N	21	shani	meer34499@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	201956b5cc04475093114ca93a440d66.pdf	23	Bs. sociology and computer	8888888	50	Partial Match. Education: 100%. CV education: ms office, ms office - the institute of i, ms excel. Experience: 66%. CV experience: 23.0 years. Relevant experience: good communication and teamwork (related). Skills/requirements: 0.0%. Missing requirements: relevant experience for the admin role, good communication and teamwork, ability to learn quickly and meet deadlines, relevant degree or equal practical experience we are looking for a admin to join our team, you will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	applied	03073674508	\N	\N	\N
26	\N	21	sami	sami123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	d0b86b365e684710902e728a16d412fd.pdf	12	BS.sociology	80000	50	Partial Match. Education: 100%. CV education: ms office, ms office - the institute of i, ms excel. Experience: 66%. CV experience: 12.0 years. Relevant experience: good communication and teamwork (related). Skills/requirements: 0.0%. Missing requirements: relevant experience for the admin role, good communication and teamwork, ability to learn quickly and meet deadlines, relevant degree or equal practical experience we are looking for a admin to join our team, you will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	applied	03012345678	\N	\N	\N
24	\N	20	kamran	kamran123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	d28f9a14e28343eab12e427b6940c4c7.pdf	3	Bs. sociology	30000	58	Partial Fit. Exact skills: communication. Missing skills: teamwork.	hired	03073674508	20000.00	2026-11-18	\N
27	\N	21	sadi	sadi123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	addf700db5f14c57a1bb8b005d32706d.pdf	12	BS.sociology	80000	50	Partial Match. Education: 100%. CV education: ms office, ms office - the institute of i, ms excel. Experience: 66%. CV experience: 12.0 years. Relevant experience: good communication and teamwork (related). Skills/requirements: 0.0%. Missing requirements: relevant experience for the admin role, good communication and teamwork, ability to learn quickly and meet deadlines, relevant degree or equal practical experience we are looking for a admin to join our team, you will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	applied	03012345678	\N	\N	\N
28	\N	21	ahadali	ahadali@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	324cadca81fa44db87c02b8377bcf475.pdf	12	BS.sociology	80000	50	Partial Match. Education: 100%. CV education: ms office, ms office - the institute of i, ms excel. Experience: 66%. CV experience: 12.0 years. Relevant experience: good communication and teamwork (related). Skills/requirements: 0.0%. Missing requirements: relevant experience for the admin role, good communication and teamwork, ability to learn quickly and meet deadlines, relevant degree or equal practical experience we are looking for a admin to join our team, you will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	applied	03012345678	\N	\N	\N
29	\N	21	nagin	nagin123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	80f3392fab82421aa7056b2ac2ca9d7f.pdf	3	Bs. sociology	30000	50	Partial Match. Education: 100%. CV education: ms office, ms office - the institute of i, ms excel. Experience: 66%. CV experience: 3.0 years. Relevant experience: good communication and teamwork (related). Skills/requirements: 0.0%. Missing requirements: relevant experience for the admin role, good communication and teamwork, ability to learn quickly and meet deadlines, relevant degree or equal practical experience we are looking for a admin to join our team, you will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	applied	03073674508	\N	\N	\N
30	\N	21	sadi	saji123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	a9eab9c89cef4b9c800f1ff76f35e266.pdf	5	BS.computer science	900000	48	Partial Match. Education: 100%. Experience: 60%. Skills: 0.0%. Missing job requirements: 8.	applied	030666666	\N	\N	\N
32	\N	22	maji	maji123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	a888f04d818b4f6a9a98f81917d0f9e5.pdf	20	BS.computer science	80000	18	Low Match. Education: 0%. Experience: 60%. Skills: 0.0%. Missing job requirements: 3.	hired	03077777	60000.00	2026-11-30	\N
31	\N	22	major	major123@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	046225907fa340a794acb14463608f43.pdf	10	BS.sociology	80000	18	Low Match. Education: 0%. Experience: 60%. Skills: 0.0%. Missing job requirements: 3.	hired	03012345678	80000.00	2026-11-22	\N
33	\N	22	saad	saad331@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	5b819e7c0d5e4e64bafbadf43181bb92.pdf	20	BS.computer science	80000	18	Low Match. Education: 0%. Experience: 60%. Skills: 0.0%. Missing job requirements: 3.	shortlisted	03077777	\N	\N	\N
35	20	21	sudheer ahmed	bk2090960@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	665f695abf944836b3b08d91410ad59a.pdf	2	Bs. sociology	30000	48	Partial Match. Education: 100%. Experience: 60%. Skills: 0.0%. Missing job requirements: 8.	applied		\N	\N	\N
42	\N	8	Mr_Lucca	khanbaba6958bjj@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	0fe642fc70b14191a60d6627abaa1682.pdf	23	Bs. sociology	900000	25	Low Match. Education: 0%. Experience: 64%. Skills: 13.6%. Missing job requirements: 9.	applied	03087654546	\N	\N	\N
34	20	22	sudheer ahmed	bk2090960@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	206379df9fe14c499b3af5dde1139325.pdf	3	BS.sociology	8888888	18	Low Match. Education: 0%. Experience: 60%. Skills: 0.0%. Missing job requirements: 3.	shortlisted		\N	\N	\N
36	20	20	sudheer ahmed	bk2090960@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	d45a7dbb604c4e048f8f3b864d189a72.pdf	30	Bs. sociology	33	48	Partial Match. Education: 100%. Experience: 60%. Skills: 0.0%. Missing job requirements: 8.	offer_pending		30000.00	2026-11-24	\N
38	\N	22	ssad ali	saad1122@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	4d2a4daf80b543a4a007d1ac956fd737.pdf	8	bs.sociology	29	18	Low Match. Education: 0%. Experience: 60%. Skills: 0.0%. Missing job requirements: 3.	shortlisted	03043772087	\N	\N	\N
40	\N	18	Mr_Lucca	khanbaba6958bjj@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	edd47836ef7744fdb2e12752b915279c.pdf	23	Bs. sociology	900000	57	Good Match. Education: 100%. Experience: 66%. Skills: 18.8%. Missing job requirements: 6.	shortlisted	03012345678	\N	\N	\N
37	\N	19	adil khan	adilhuzaaifa@gmail.com	ZAFARULLAH\n Shaheed Shah Inayat Society, Karachi\n +92 307 3674508 | meer34499@gmail.com\nOBJECTIVE\nAn entry-level Data Officer position where a Sociology background, an understanding of social trends,\ncommunities and research methods, together with strong record-keeping, documentation and MS Office\nskills, is needed to collect, organize and maintain accurate, reliable data.\nEDUCATION\nUniversity of Karachi, Karachi — B.Sc. Sociology (Anticipated graduation: Nov 2026)\n  Coursework includes Human Resource Management (Oct – Dec 2025)\nEXPERIENCE\nHRM Intern (Remote), xLoop Digital — Sep 2026 – Present\nSubject Teacher, St. Jacob Grammar School, Karachi — Sep 2025 – Feb 2026\n  Organized schedules and class information for multiple classes, working to daily deadlines.\n Entered, updated and maintained accurate student records and documentation.\n Reported information clearly to students, parents and staff and resolved queries professionally.\nTeam Coordinator (Volunteer), Sindh Child Protection Authority — Nov 2024\n  Led a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n Kept project schedules on track and productivity high.\n Handled conflict resolution and team communication.\nTeam Coordinator (Volunteer), DOPASI Foundation — Nov 2024\n  Coordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n Delivered key project objectives on schedule through task allocation and progress monitoring.\n Built hands-on experience in leadership, event planning and managing diverse groups.\nSubject Teacher (Social Studies / Pakistan Studies), Seerat Public School — 2023 – 2024\n  Managed classroom scheduling and designed course plans.\n Maintained records and administrative data using MS Office.\n Prioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nCERTIFICATIONS AND COURSES\n  AI Agentic Training Program, xLoop Digital — Apr – Aug 2026\n Human Resource Management, University of Karachi — Oct – Dec 2025\n MS Office, The Institute of I.T & Multimedia — Jun – Aug 2025\n Certificate in Information Technology (C.I.T), Crown Institute of Science & Technology — Jul –\nDec 2024\nSKILLS\n  Software: MS Excel, Word and PowerPoint (Intermediate)\n Data: Data entry, record-keeping and documentation\n Abilities: Accuracy and attention to detail; scheduling, planning and time management;\ncommunication and team coordination\n Technology: AI agentic tools and basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	3ba6af79822c44e5850800457635e1fd.pdf	2	undereducate	2345	57	Good Match. Education: 100%. Experience: 66%. Skills: 18.8%. Missing job requirements: 6.	offer_pending	123456789	12345.00	2026-11-22	\N
39	\N	22	Mr_Lucca	khanbaba6958bjj@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	d8ed096ca20c405bac4d294cbe108b2d.pdf	8	BS.computer science	33	18	Low Match. Education: 0%. Experience: 60%. Skills: 0.0%. Missing job requirements: 3.	applied	03012345678	\N	\N	\N
41	\N	17	Mr_Lucca	khanbaba6958bjj@gmail.com	ZAFARULLAH\n Data Officer Candidate | B.Sc. Sociology, University of Karachi\n Shaheed Shah Inayat Society, Karachi  |  +92 307 3674508  |  meer34499@gmail.com\nSUMMARY\nDetail-oriented final-year B.Sc. Sociology student with hands-on experience in record-keeping, documentation\nand MS Office, backed by an IT certificate and recent AI training. Known for accuracy, meeting deadlines and\ncommunicating clearly. Seeking a Data Officer role to collect, organize and maintain reliable data.\nEDUCATION\nB.Sc. Sociology — University of Karachi\n Expected November 2026\nCERTIFICATIONS & COURSES\nAI Agentic Training Program — xLoop Digital\n Apr – Aug 2026\nHuman Resource Management — University of Karachi\n Oct – Dec 2025\nMS Office — The Institute of I.T & Multimedia\n Jun – Aug 2025\nCertificate in Information Technology (C.I.T) — Crown Institute of Science &\nTechnology\n Jul – Dec 2024\nWORK EXPERIENCE\nHRM Intern (Remote) — xLoop Digital\n Sep 2026 – Present\nSubject Teacher — St. Jacob Grammar School, Karachi\n Sep 2025 – Feb 2026\n\nOrganized schedules and class information for multiple classes, working to daily deadlines.\n\nEntered, updated and maintained accurate student records and documentation.\n\nReported information clearly to students, parents and staff and resolved queries professionally.\nSubject Teacher (Social Studies / Pakistan Studies) — Seerat Public School\n 2023 – 2024\n\nManaged classroom scheduling and designed course plans.\n\nMaintained records and administrative data using MS Office.\n\nPrioritized tasks and met strict deadlines in a high-volume, detail-oriented environment.\nVOLUNTEER EXPERIENCE\nTeam Coordinator — Sindh Child Protection Authority\n Nov 2024\n\nLed a team of 15+ volunteers, tracking task progress and performance to keep work accurate and on\nschedule.\n\nKept project schedules on track and productivity high.\n\nHandled conflict resolution and team communication.\nTeam Coordinator — DOPASI Foundation\n Nov 2024\n\nCoordinated a volunteer workforce of 20+ for TB awareness programs and educational seminars.\n\nDelivered key project objectives on schedule through task allocation and progress monitoring.\n\nBuilt hands-on experience in leadership, event planning and managing diverse groups.\nSKILLS\n Data entry, record-keeping & documentation\n MS Excel, Word, PowerPoint (Intermediate)\n Accuracy & attention to detail\n Scheduling, planning & time management\n Communication & team coordination\n AI agentic tools & basic IT (xLoop training, C.I.T)\nREFERENCES\nAvailable on request.\n	8d6ec2db93f64df481ebaa85538f799d.pdf	23	Bs. sociology	900000	48	Partial Match. Education: 100%. Experience: 60%. Skills: 0.0%. Missing job requirements: 8.	applied	089009099	\N	\N	\N
\.


--
-- Data for Name: company_info; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_info (info_id, company_name, about_us, mission, address, website, contact_email, updated_by, tagline, vision, services, team, phone, facebook, linkedin, instagram, twitter) FROM stdin;
1	Tech solution Provider	xLoop is a global AI and data consulting firm, serving Fortune 500s, startups and public sector clients worldwide. We specialize in Gen AI, Computer Vision, AI Security and end-to-end data management solutions, partnering with leaders who want to win.	Our mission is to build technology that helps businesses grow, and to build a team of talented people by giving every candidate an equal and honest chance to be hired.	1st Floor, Marine Tower, Block 4 Clifton, Karachi Pakistan	https://www.xloopdigital.com/	xloop@gmail.com	1									
\.


--
-- Data for Name: email_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.email_codes (code_id, email, code_hash, purpose, expires_at, wrong_tries, used) FROM stdin;
1	mrluca607@gmail.com	da9f5fa9b4be63bff260d1bda670a805b303d894ed767330ad545576acf23982	signup	2026-10-29 03:53:32.678514	0	t
2	mrluca607@gmail.com	ecc861105be790eece3a6e0a9526db97c32d5c8d8a786e40e3290e6bed0b965b	signup	2026-10-29 04:05:54.219012	0	t
3	mrluca607@gmail.com	fd9ff2bbbae5dfbaebcd8e4a6e5a7b5b78919392435af5401538faf9e7b07e2d	signup	2026-10-29 04:07:38.550742	0	t
4	huzi123@gmail.com	c415b8919ceeac5b64c3af4e14c033e729ace2a77d5628dc10010e7cb7dcfcab	signup	2026-10-29 06:20:05.314671	0	t
5	haseebmalikgoto@gmail.com	f2ba8cc13fc432db18b4a6017599803115f9c19d057e4ef3e59ee47dcf829f34	signup	2026-10-30 02:29:34.496985	0	t
6	hhaseebzafar3@gmail.com	7d4bde5b024c2ae991944dc97304870361fdd71863e2760ec0575941bfafc946	signup	2026-10-30 02:34:32.154187	0	t
7	hhaseebzafar3@gmail.com	8a502220f1b8d7f21855350257551c44d341c40dd0a9dafb86e2445e9dfa2c06	signup	2026-10-30 02:38:13.872275	0	t
8	hhaseebzafar3@gmail.com	ce3bb5480cd7043991e6e2d1db5482f4acc1b7097a13371bdffd7fe345659276	signup	2026-10-30 02:52:34.871646	0	t
9	sadammahar500@gmail.com	aa69e312ee3f99b2828a9cdcefb4999f2349503095a90f8eb94e43b1028ea92c	signup	2026-10-31 07:02:32.95528	0	t
10	sudheer@gmail.com	fc5d4e4e9ca7114ac6462af99b9a2d70869124f5b99a827e16dad0745cc4d1a3	signup	2026-11-01 00:00:34.139435	0	t
11	haseebzafar3@gmail.com	ed4c3e022fca4c692dad6a2dcf7863cec1f4073a25e3a01eed7dcb784f392513	signup	2026-11-01 23:26:54.329597	0	t
12	sajid123@gmail.com	4daba9716f6e8f84d2950e7c1d4cfb790acbd945db0c1d9aec2d936499ffe7a2	signup	2026-11-06 02:33:34.762524	0	t
13	sajid123@gmail.com	ca6a88bcbcbdbaee9fee50e0adefcf292c88f64c3b025fccb5fdf1edf6e0d9b1	signup	2026-11-12 01:47:31.605561	0	f
14	ali123@gmail.com	9295c228ecde7ea495b4b493bacc14c01e70418057edfb825f89b6e2cf01f85e	signup	2026-11-19 00:42:08.312135	0	f
15	shahu123@gmail.com	842acc4d31c2702d8c0da357555c908fb8d459b941a06d132b4d62d5698576d5	signup	2026-11-20 02:22:10.777618	0	t
16	meer2299@gmail.com	ff631e3167cb3e646083a95338f2fca9944e614b1cf7c43757f9b2a9f908178b	signup	2026-11-20 04:39:30.013243	0	t
17	maharasad@gmail.com	34d47a5b5f853237db62e82f2c3077f8d5d4a958106bee00eb8781b87c849ab7	signup	2026-11-20 05:45:43.184273	0	t
18	maharasad@gmail.com	f377b1d0595411e7d92141c2a85898de2fa31e90089b7f1b5997aab622eb3507	signup	2026-11-20 06:01:58.237971	0	f
19	maharasad485@gmail.com	1894e39305a6bf36fa67e9fa48444da6b2d4251d8561dcfa364895acd2d9b3bf	signup	2026-11-20 06:04:12.910088	0	t
20	maharasad485@gmail.com	d36446d0a41523fa40067491b9b36b27e152bd16496a49f41ffad38efd982717	reset	2026-11-20 06:54:41.842863	0	f
21	bk2090960@gmail.com	f2d4fc5df0d6769c31299f24331a04ea0db3a81eecb3e614f9c5a5170b89a1c9	signup	2026-11-20 07:05:58.749226	0	t
22	adilhuzaaifa@gmail.com	22a9bc245292212895d0d199fa2ff00d2cb6a02031b3ae4672716f2355ea41ad	signup	2026-11-20 08:55:59.924687	0	t
23	khanbaba6958bjj@gmail.com	50541b24419ff9b25cc224702892256cfdb5ac2eb7ac6295c6156365934fea69	signup	2026-11-22 12:42:19.901141	0	t
\.


--
-- Data for Name: interviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interviews (interview_id, candidate_id, interview_date, feedback, rating, instructions) FROM stdin;
1	1	2026-11-15 14:20:00	\N	\N	\N
2	2	2026-11-10 02:00:00	\N	\N	\N
4	4	2026-11-18 13:23:00	\N	\N	Please bring the following documents:\r\n- Original CNIC\r\n- Original academic certificates and degrees\r\n- Experience letters from previous employers\r\n- One printed copy of your CV
7	8	2026-12-12 12:00:00	good communication	4	Please bring the following documents:\r\n- Original CNIC\r\n- Original academic certificates and degrees\r\n- Experience letters from previous employers\r\n- One printed copy of your CV
6	9	2026-12-12 10:12:00	good	3	Please bring the following documents:\r\n- Original CNIC\r\n- Original academic certificates and degrees\r\n- Experience letters from previous employers\r\n- One printed copy of your CV
5	6	2026-12-12 14:11:00	has been selected	4	Please bring the following documents:\r\n- Original CNIC\r\n- Original academic certificates and degrees\r\n- Experience letters from previous employers\r\n- One printed copy of your CV
3	3	2026-12-12 13:56:00	good	4	Please bring the following documents:\r\n- Original CNIC\r\n- Original academic certificates and degrees\r\n- Experience letters from previous employers\r\n- One printed copy of your CV
9	19	2026-11-22 15:17:00	he was good	4	bring original documents
11	21	2026-11-24 20:32:00	good	4	Interview type: in_person\n\nInterview notes:\nbring nothing
10	20	2026-11-17 17:54:00	good	5	Interview type: online\n\nInterview notes:\nno
12	22	2026-11-17 18:35:00	saas	3	Interview type: online\n\nInterview notes:\nbring nothing
13	24	2026-11-18 15:11:00	good	4	Interview type: online
15	32	2026-11-19 17:08:00	good	2	Interview type: online
14	31	2026-11-19 16:57:00	bring nothing	1	Interview type: online
16	33	2026-11-22 21:31:00	\N	\N	Interview type: in_person
17	36	2026-11-22 23:50:00	was good	2	Interview type: online\n\nInterview notes:\nbring nothing
18	37	2026-11-22 12:52:00	good experience	4	Interview type: online\n\nInterview notes:\nwant a jov'
8	17	2026-11-16 13:18:00	good	4	Interview type: online\n\nInterview notes:\nbring org
\.


--
-- Data for Name: job_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.job_questions (question_id, job_id, question_text) FROM stdin;
1	10	How many years of experience do you have for the Subject Teacher , English role?
2	11	name
7	14	How many years of experience do you have?
8	14	name
11	15	How many years of experience do you have for the Full stack developer role?
12	15	Which skills from the requirements are your strongest? Give one example of your work.
13	15	Why do you want to join our company?
14	15	What is your expected monthly salary?
15	15	When can you start working with us?
16	17	How many years of experience do you have for the Team lead role?
17	17	Which skills from the requirements are your strongest? Give one example of your work.
18	17	Why do you want to join our company?
19	17	What is your expected monthly salary?
20	17	When can you start working with us?
21	18	Name
22	18	cnic
23	18	experience
28	19	Name
29	19	CNIC
30	19	How many years of experience do you have for the Subject Teacher , English role?
31	19	Skills
32	20	Name
33	20	CNIC
34	20	Qualification
35	21	How many years of experience do you have for the Subject Teacher , English role?
37	22	if experienced, define previous role
40	23	why are u interested ?
41	24	Describe your previous experience
44	25	How many years of experience do you have for the Subject Teacher , English role?
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.jobs (job_id, title, department, salary_range, location, description, requirements, benefits, deadline, poster_path, created_by, status, reject_reason, approved_by) FROM stdin;
18	Teacher	Admin	10000	sukkur	We are looking for a Teacher to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Teacher role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	published	\N	5
1	Python Developer	IT	20000	karachi	ndjn	JDNJ	NDJ	2026-11-12	\N	1	closed	\N	5
11	desk		20000	karachi	jhguy	hj	jkh	2026-12-12	\N	1	published	\N	5
10	shahid	dsd	20000	karachi	dsd	fdsd	sfasf	2026-12-12	\N	1	published	\N	5
9	security guard	security	10000	karachi	must have licence	exeperience	good salary	2026-12-12	\N	1	published	\N	5
3	HR	people and culture	10000	karachi	required a high qualified	ms in hr	competitive salary	2026-11-01	\N	1	rejected	yufdyef	5
8	Subject Teacher , English				We are looking for a Subject Teacher , English to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Subject Teacher , English role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	\N	\N	1	published	\N	5
13	Head of the department				We are looking for a Head of the department to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Head of the department role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	\N	\N	1	draft	\N	\N
7	HR				We are looking for a HR to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the HR role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	\N	\N	1	published	\N	5
14	Researcher	Sociology	20000	karachi	We are looking for a Researcher to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Researcher role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	published	\N	5
6	clerk	IT	20000	karachi, sukkur	We are looking for a clerk to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the clerk role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-11-12	\N	1	published	\N	5
15	Full stack developer	IT	20000	karachi	We are looking for a Full stack developer to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Full stack developer role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-11-12	\N	1	published	\N	5
5	Full stack developer	IT	20000	sukkur	We are looking for a Full stack developer to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Full stack developer role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-11-01	\N	1	published	\N	5
17	Team lead				We are looking for a Team lead to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Team lead role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	published	\N	5
19	Teacher	pakistan studies	20000	karachi	We are looking for a Teacher to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Teacher role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	published	\N	5
2	full stack developer	it	10000	karachi	we want a developer with three yeAR Experience	matrix	compitive salary	2026-11-01	\N	1	published	\N	5
20	Clerk	it	20000	karachi	We are looking for a Clerk to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Clerk role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	published	\N	5
21	Admin	Office	20000	karachi	We are looking for a Admin to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the Admin role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	published	\N	5
22	full stack developer	IT	100000	sukkur	backend,\r\nwebsite creator,	BS. computer science or related field	comitative salary	2026-12-12	\N	1	published	\N	5
23	AI Agentic	IT	100000	sukkur	We are looking for a AI Agentic to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the AI Agentic role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	closed	\N	5
25	Researcher	Sociology	800000	karachi	we need a researcher, data analysis	DEGREE BS	COMPITIVE SALARY	2026-12-12	\N	1	published	\N	5
24	softaware engineer	AI	10000	karachi	We are looking for a softaware engineer to join our team. You will work with colleagues on real projects, take ownership of your tasks, and help us deliver quality results for our clients.	- Relevant experience for the softaware engineer role\r\n- Good communication and teamwork\r\n- Ability to learn quickly and meet deadlines\r\n- Relevant degree or equal practical experience	- Competitive salary\r\n- Learning and growth\r\n- Friendly team\r\n- Medical cover	2026-12-12	\N	1	rejected	LOOK BEFORE LEAP	5
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (notification_id, to_role, to_user_id, message, job_id, is_read, created_at) FROM stdin;
12	\N	1	Your job was approved and published: desk	11	f	2026-10-31 00:30:36.178219
11	manager	\N	New job waiting for your approval: desk	11	t	2026-10-31 00:20:54.391277
13	\N	1	Your job was approved and published: shahid	10	f	2026-10-31 00:30:46.564835
10	manager	\N	New job waiting for your approval: shahid	10	t	2026-10-31 00:05:25.585399
14	\N	1	Your job was approved and published: security guard	9	f	2026-10-31 00:30:52.540655
9	manager	\N	New job waiting for your approval: security guard	9	t	2026-10-31 00:04:01.583155
16	\N	1	Your job was approved and published: Subject Teacher , English	8	f	2026-10-31 01:11:48.204601
8	manager	\N	New job waiting for your approval: Subject Teacher , English	8	t	2026-10-30 23:27:02.14144
18	\N	1	Your job was approved and published: Researcher	14	f	2026-10-31 01:47:41.232819
17	manager	\N	New job waiting for your approval: Researcher	14	t	2026-10-31 01:47:15.782426
20	\N	1	Your job was approved and published: Full stack developer	15	f	2026-10-31 07:01:54.297215
19	manager	\N	New job waiting for your approval: Full stack developer	15	t	2026-10-31 07:00:53.517313
21	\N	1	Your job was approved and published: Python Developer	1	f	2026-11-05 00:29:01.015354
2	manager	\N	New job waiting for your approval: Python Developer	1	t	2026-10-30 02:16:31.057809
23	\N	1	Your job was approved and published: Team lead	17	f	2026-11-06 02:48:00.072144
22	manager	\N	New job waiting for your approval: Team lead	17	t	2026-11-06 02:28:44.258657
24	\N	1	Your job was approved and published: HR	7	f	2026-11-13 00:33:40.046041
7	manager	\N	New job waiting for your approval: HR	7	t	2026-10-30 23:13:07.020697
25	\N	1	Your job was approved and published: clerk	6	f	2026-11-13 01:00:10.580959
6	manager	\N	New job waiting for your approval: clerk	6	t	2026-10-30 03:11:59.370426
26	\N	1	Your job was approved and published: Full stack developer	5	f	2026-11-13 01:27:44.702516
5	manager	\N	New job waiting for your approval: Full stack developer	5	t	2026-10-30 03:06:35.568334
27	\N	1	Your job was rejected: HR. Reason: yufdyef	3	f	2026-11-13 01:27:58.935974
3	manager	\N	New job waiting for your approval: HR	3	t	2026-10-30 02:57:28.868992
29	\N	1	Your job was approved and published: Teacher	18	f	2026-11-13 01:38:18.651874
28	manager	\N	New job waiting for your approval: Teacher	18	t	2026-11-13 01:37:55.451882
31	\N	1	Your job was approved and published: Teacher	19	f	2026-11-16 05:45:59.866205
30	manager	\N	New job waiting for your approval: Teacher	19	t	2026-11-16 05:45:24.388869
32	\N	1	Your job was approved and published: full stack developer	2	f	2026-11-16 23:55:21.591326
1	manager	\N	New job waiting for your approval: full stack developer	2	t	2026-10-29 07:10:53.26859
34	\N	1	Your job was approved and published: Clerk	20	f	2026-11-17 01:06:15.155893
33	manager	\N	New job waiting for your approval: Clerk	20	t	2026-11-17 01:05:35.245091
36	\N	1	Your job was approved and published: Admin	21	f	2026-11-17 02:17:08.469175
35	manager	\N	New job waiting for your approval: Admin	21	t	2026-11-17 02:16:41.558216
38	\N	1	Your job was approved and published: full stack developer	22	f	2026-11-17 02:46:11.528705
37	manager	\N	New job waiting for your approval: full stack developer	22	t	2026-11-17 02:45:25.13014
40	\N	1	Your job was approved and published: AI Agentic	23	f	2026-11-19 04:48:31.53365
39	manager	\N	New job waiting for your approval: AI Agentic	23	t	2026-11-19 04:48:10.414463
43	\N	1	Your job was approved and published: Researcher	25	f	2026-11-22 12:56:07.711484
42	manager	\N	New job waiting for your approval: Researcher	25	t	2026-11-22 12:55:39.129726
44	\N	1	Your job was rejected: softaware engineer. Reason: LOOK BEFORE LEAP	24	f	2026-11-22 12:56:24.415474
41	manager	\N	New job waiting for your approval: softaware engineer	24	t	2026-11-20 03:16:58.508717
\.


--
-- Data for Name: offers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.offers (offer_id, candidate_id, offer_status, offered_salary, joining_date, offer_token, sent_at, responded_at) FROM stdin;
2	20	accepted	3000	2026-11-26	5F6Lo4aGL1XWdBpADZh0jxOg7YBFDYfVEPsbqDAM9Ws	\N	2026-11-16 00:58:08.122506
1	21	rejected	200000	2026-11-30	PwMDbZPxZjwk3sAysZXZIEOYxkTMB5RFGUzJ3ZN3IWE	\N	2026-11-16 01:10:52.375003
3	24	accepted	20000	2026-11-18	jwJwwOkPZ-4_Xf3VYaRd-o_yyHBALUlZE5l6-3abAcg	\N	2026-11-17 01:12:28.78621
4	32	accepted	60000	2026-11-30	0O_Iui1uMt_IV6Q4NSOqJmv4GaKFVHQKbXy09i3pRCQ	\N	2026-11-18 01:27:48.863627
5	31	accepted	80000	2026-11-22	4wEuo0EaLbsmNsUCROhrf_f4ykFKtf03mnkBT_boddg	\N	2026-11-19 02:17:32.354097
6	36	pending	30000	2026-11-24	LwyzTSsTri93iuHuDidgmcacUAJVrt6ETWeuehxHGW4	\N	\N
7	37	pending	12345	2026-11-22	hOFwM9o2giB2qPvkQCroXypiHDDbbgzm9t8DDt29vWE	\N	\N
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_resets (reset_id, email, code_hash, expires_at, used, created_at) FROM stdin;
\.


--
-- Data for Name: role_invites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_invites (invite_id, email, role, invited_by, status, created_at) FROM stdin;
1	huzi123@gmail.com	manager	1	accepted	2026-10-29 06:40:38.597288
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sessions (token, user_id, created_at) FROM stdin;
7c694cf782554e1b6dd66519dfaa395f009627946a796dca8aabb62d1e1ff077	5	2026-11-20 08:47:49.640078
692e66c4fc923a4f4b9db93bbb7816e934707650b40ae45d124d57e54b207045	1	2026-11-20 08:58:03.809389
5330b972c9c45e249ba5750eac4219bc816e36621353b4d6153ac2c3bb798fc0	22	2026-11-22 12:32:44.787653
5fa75443cd616ba6ae75403e054c2181020ae352c68581936a7d02341f858975	22	2026-11-22 12:35:29.977705
e9a6fac1f8e8fea0c8e7d528fa6ce4ebeb022558bc616f977c7f617a59767a73	22	2026-11-22 12:43:27.511519
184d9a27fd56278d2ee96de1640325268cfd8b8533b5405274974f490f2c5652	22	2026-11-22 12:47:18.714103
321a44044cb933ed03785ecd1fac18e999f7fc172195ceb79ac23ecd8b96b74b	1	2026-11-06 06:57:18.946574
cd1b2b06fd152d4b6b5517d769339da4894112cbd51e3f31bad470ffd609f484	1	2026-10-29 07:16:03.725516
3f3f11b4f83a18953f59c16bafcbb3e5be38b5b4f9f3b88e842e2ef793063c17	1	2026-11-11 02:55:36.910308
14af419eb444a6afa3f0f92f9aa20b751b22282d6799ac40b14fefce21e24c47	1	2026-10-30 02:56:26.702371
d4f43a34025e47f78ad035a1ef54e5f2124c488bdd16626d01b47119b0b7438a	1	2026-10-30 03:10:01.889469
badd93c9464d843917bd0c18831e830b3b1940a398acd037bb405a2943a34cf5	21	2026-11-22 13:01:50.689718
48d6c9f2a8f44ba7f1e452dfda71ae1e8c89f4c414d399ecb321a5f59a0b609e	21	2026-11-22 13:03:19.057482
a5ce285d26ecae0983a5e63307d48cb87e180aecb4003f41461225fb67b8c4fa	1	2026-11-22 13:04:27.016503
938a272645557bae413b816c0608cfa5071285c48edf233407a2921cf5e59f7e	1	2026-11-12 06:08:35.62649
08330660f1bddcc6585490403e292c8962623021bf0a451116b57a7aaae71caa	5	2026-11-12 22:22:52.10843
0a57cbbe26400dd24970c94748dbe3ab87df9b96452f20ca38bc6926c33b6e4c	1	2026-11-12 23:59:46.918357
1719357d840853cea9ca47362d2f3640b83ab9308155f6b791c14b12168255f0	1	2026-11-13 00:12:59.077546
5477c7d8327c4727365c70acc3ab1415ee82b77488f54fde87e3c3a5bc50dd7e	5	2026-11-13 00:13:09.519429
b34307e47c874fe8df5af0706a77eac7c7c2458f4cd05850cb19f2ea07b09323	5	2026-11-13 00:14:31.785529
0dd9d5e9caa92974e5d19ed84809643ed0d86f71289b3ac3a7b2c8a44612f6fe	5	2026-11-13 00:24:32.648164
69d9451f9bd404252e85fae6ed4747ac4e9df8cc1d1827bd87885e7dc8501094	1	2026-10-31 03:52:06.840154
02b6ec15a74621e668718b079102ab0148774610acb49b75ffafaa359371c4ba	5	2026-11-13 00:26:14.321756
5231a4c2e8bd3e5566e5e650303f40b6cf5f93e0c06b20a55dd62ab01523276d	5	2026-11-13 00:29:18.053164
62b5d61bfb33d9b4251f1a453894b6f7f9cd5f76884e71de76ea0bcb37dd09e1	5	2026-10-31 07:01:24.908166
2affdec5d86298e0ce5b695eadb4541c840dcbac80cce5c59011a220818687e1	5	2026-11-13 00:30:31.532386
8c58b7b24869d9325dce564a05bab3e14ee540c6f0353ed417cfe093e5ae2cd7	5	2026-11-13 00:31:18.066087
6ab1cdc03d7b27634a59e400443e68dfbec0ce1d1060a8dd4f4ebb7002c51bd8	1	2026-11-13 00:50:42.107232
316b14460422383f215b30582c3d9d1db6755cc37fd2d9d09dcce4eedcefa7f5	5	2026-11-13 00:55:43.174227
81483074728fcb95853df9e010ef2679d2973810b2f44af9a8ea95ea2dbcc5ab	5	2026-11-13 00:58:34.039961
e8e12daf8558d4413fe1238c430484c1c5128b587d36f39b100475eac6c46bfc	5	2026-11-13 01:38:09.478573
a4c131c47548c5427c59c8ab6ae007052ae6f13d9c3327ba78ac12189a9c4cc0	1	2026-11-01 01:02:14.440532
3ef7d039f01ae0485f38fe96432a8b26a080ea424f894f10525921016283f386	1	2026-11-13 01:49:08.332906
b2c5438f351245e8346059d2c1edb9d17812d91f524f46b5336089f9d0b83e58	1	2026-11-14 01:20:54.889232
8753cff11c1042af202d757bbc9cee68354e888c05ecae64b7a7092a1ff17e22	1	2026-11-14 04:42:03.455089
d06e30bc5438f95b39b62df5744c61ddc3b1e99761a9c9e7560030bb41fd5fc1	1	2026-11-15 00:20:42.197447
0e8259bd71838d32d172fe0d5d3cb15684d6e3c1c1a90af15634987cd89eea03	1	2026-11-01 23:22:54.216473
8790c8f972dfc8833f1e09fd3cf019fccb4a5f0c559e29dd34bd9e1c2badfb8a	1	2026-11-15 02:31:54.044275
e2427ece26c3ef395cb1e7c5cd55daa73114179ccfa6304fbc173c8c5d56884d	1	2026-11-01 23:24:59.568179
64e35872560575663fa6208efd357d19009e0908dd58f6283f61340da1549e10	9	2026-11-05 00:29:22.838931
f67e5c06c928add8af13ce9ec9b91fb02ac389e1b1f35ea7c8ef69136fdb3093	5	2026-11-16 05:45:41.48656
a6467355cc7dd85f0e41a239a2fb40ce230e647edbfe0b5f98dfe5a3bc03538d	5	2026-11-16 05:47:40.908444
1f38faf6a7be78ea702d8a861d52971a7dd3687a876bf1c56a22fda1c1eeaaed	1	2026-11-05 08:45:32.248171
1468ebc1552073e98176209bfdcd87c7133bd068d98a7bd97b333156d441abc7	1	2026-11-16 05:50:15.254432
f738ec4f4881ca3670889edabdae52fec7c7b4e7aca0d5a19fdddc2b18c49809	8	2026-11-05 12:12:09.621133
c47823106622ec19880e8bf7988562328bbf5978f314d8f5e7d41b1b35090485	5	2026-11-16 23:55:01.462258
d0ed33b49ffae590731a4753429fcc0d071518172fcd1c0e4b00693a4f18ae8d	1	2026-11-17 00:04:28.593794
a0bbfcc450919082cf12625c408b7ac108909fa66c349aa1730b7175a2a92d24	1	2026-11-17 00:28:11.603017
0f3a46997c889220c126f08c6651a342e0f9f7d7ed40bd8de901786ed3d0ec3d	1	2026-11-17 00:33:36.644435
a08c3d62cf248848738c06c0ba613a6d7d0f93b463b5d55535a41a6a1d57d080	1	2026-11-17 00:47:12.410684
2b77fc5d1083759fb9e00a3e2f6d5a0f835f144f50c33be141fb879a8be24513	5	2026-11-17 02:29:01.109816
43af947e84347320531a136b5789b140f2fb1a60e888e32c9a3685565d2c2646	1	2026-11-17 02:48:40.077054
b563e2a774ad6c747d34bad1a03688f3feff7ef5820c5a42597ad95c534214e5	1	2026-11-17 03:02:55.717553
436500e7af2ff3afe212c069a51b9b02c359ce1abc995a0da957404ced4ee10a	1	2026-11-17 23:22:07.760108
f601dae710d1cc73e6946086fe0605fd46fa3dbb17623a24d13018e6c7a662ca	1	2026-11-18 01:34:03.070947
afa66f352f2e9d91ff2aa6956889b1bb06e85773bad8a0ed084cea20b87d1b68	5	2026-11-19 04:48:22.447901
3a0b78590d5596e6ea4d0642b883e058053085540972aa3d7941ed42bf5eb205	1	2026-11-19 23:50:17.938773
2de6fcb9ec5cf8d20e9a53fb34f6c51cb92e71558ab589165dddfc083ae02b3d	15	2026-11-20 02:19:42.577848
3f23b169232734f848b8c4aa6ae3359421b2cc7ae446b158a6286c48e50b2ec2	1	2026-11-20 03:17:09.030255
1609a58896689a228f378e2936c57a1969e7eb6526fa80ae2dc3d296ac1effd7	5	2026-11-20 03:29:40.239699
2a0e143b7552ed9ccfe1db6187e60722deb0260f91b158d09bea42e7304695bc	5	2026-11-20 03:31:11.684652
e12d1fba02ce0cfc27b225a49cc3b0de0cf805062e98c8276c61ec3622107f3a	16	2026-11-20 04:29:58.224251
c3000a05b6eb0300d3e3c6b093bdc9c14f4bd63c78d58550f7087fa77c580f99	16	2026-11-20 04:34:17.875297
2590c8e952633e5407ed26019a143725c2643e575778ef243504dbded8b66e4c	16	2026-11-20 04:47:02.243614
5a687610d773516984a03db532fd1248c21fdee8651ee56d84cc03501af4aabf	5	2026-11-20 04:47:16.320153
fe6d30f2265e76fa5c693dffc035c7cd60803420233b1f2f1ee94abda0c7cc68	18	2026-11-20 05:56:30.435681
080e54fba8250a18ffd545574199321de3f291ebc0ffac517aa23e8f40453cf0	20	2026-11-20 06:56:30.942303
573e3d1a0cc6abd72e5e9908745142467a6dc9b2e35c42a34723854d2d8eea6b	20	2026-11-20 07:29:05.588352
a0de5143fbd667d94f72da7d335f3b5544b9073e409971cca8d9db18be9d0205	1	2026-11-20 07:48:48.163296
76956f1a719ce36529ebfb6f74982a6382b3686633b72a31b95732a7d93ebe03	21	2026-11-20 08:47:16.09595
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, name, email, password_hash, salt, role, email_verified, created_at) FROM stdin;
22	Mr_Lucca	khanbaba6958bjj@gmail.com	2dbac291d526b0a1dc9c15f4313405caa5f4883d458a4a08efa35933dab116df	b8e62cf9633dc7ef6f3939ebb14eba1a	candidate	t	2026-11-22 12:32:19.673432
2	shahid	mrluca607@gmail.com	1240842299cd87ff283895894c52a9bd1d404e67a2893929e3c03c7dce99acf1	e76580b14dcf67c79879b45a95bd3540	candidate	t	2026-10-29 03:43:32.534764
5	huzi	huzi123@gmail.com	3cbf67f32b41d809d23dc45e10240982ff4be8542cab263eadc57ddcd3c45e60	28fc713a4c5b78bd2057b3aa5701cb60	manager	t	2026-10-29 06:10:05.121996
6	haseeb	haseebmalikgoto@gmail.com	c84854a6ef37e7b84c94689e069759784f91cbe7b601598b2ac469c347df234b	f3987dae3af324afbebffb73768647b4	candidate	t	2026-10-30 02:19:34.360167
7	haseeb	hhaseebzafar3@gmail.com	4711a37bc8f330ceb5dd9a5fbf3b7f70ca7cfe2d8426ec4cfb7c70a34695b65c	3b6750cd256e8ba04e9bfe83aa6eb0b3	candidate	t	2026-10-30 02:24:32.033266
8	saddam	sadammahar500@gmail.com	88b538fc8252e4f7de1a42f71e0bd4576f5d39b1cd0ead21c2aa132600eb698f	d1ee50151a6e464aaa10e84057fd75c8	candidate	t	2026-10-31 06:52:32.69157
9	sudheer	sudheer@gmail.com	f909be58c8b9649869fdc0ae318b2ff33efffc40d1f4528b1436fd86d9f5bb23	3113b702cc03983264c0c863baefe83a	candidate	t	2026-10-31 23:50:34.063545
10	zahid	haseebzafar3@gmail.com	4fa8a28fb395fa26658d869a1e195e3d55bed536164d64e3bb763ce43af22438	284edc1e47a59fcfeab21818712de13c	candidate	t	2026-11-01 23:16:54.194966
13	zafar123	sajid123@gmail.com	7a15178fe4a57253657526a21bd304a1a1d49ef4230210d9603e8dd3079b935b	c54ba98f9a1ceccbca4464078e2b1e0d	candidate	f	2026-11-06 02:23:34.567972
14	saad	ali123@gmail.com	0f9956b412425308fff9ce94f895f44e0d1b8cff35f8bb1cbf5deee177dd8508	ef18493ccd4c88d77c2d57f6a2e6373f	candidate	f	2026-11-19 00:32:08.227445
15	shahid	shahu123@gmail.com	c26862ac8d334a0a6d0b830c6431b8021f675316a68042e0b7c5fe4f99b9656e	adf57bd1d03299117506dfaee3377180	candidate	t	2026-11-20 02:12:10.635972
16	saad	meer2299@gmail.com	9206c02ad15add0d92a80bd6476c17469be16290b467f35833e0a1846b6c4b60	a807abddfa0ebdf1338c0215e35fc038	candidate	t	2026-11-20 04:29:29.890958
17	asad	maharasad@gmail.com	6d9910a9bbc70350b66aebaa214acf9b63795edec8047a333a7ec0e7cf498a40	439727e31190c294d30a8dd64b09e6c8	candidate	f	2026-11-20 05:35:42.999949
18	asadullah	maharasad485@gmail.com	ef17668691d5ee9d14b5dab44ffea50dc67c35cd04fd531e245159c5348e4605	636b807d33baa8a73d518ff77ac79f25	candidate	t	2026-11-20 05:54:12.722401
1	xloop123	meer34499@gmail.com	458975e807fead2cd6e9630e22aef9979c4154a35c14735003c176ffc426c986	f6f86b1ebaf8a2003855137fe0a73ea5	hr	t	2026-10-29 01:42:30.352877
20	sudheer ahmed	bk2090960@gmail.com	3ba3efb0031d8587d1bc3fd970f4671f447614f729138f7df56f55a6ba8e8e8e	774369ca9530dd5b7404ee0a6500d40c	candidate	t	2026-11-20 06:55:58.61202
21	adil khan	adilhuzaaifa@gmail.com	1f8f8b223091271ea7d3ef370debbdf8ecc3f943c3860f910086b852d45c2c96	ffd1cde0282cbf6f483557626f49942d	candidate	t	2026-11-20 08:45:59.776445
\.


--
-- Name: apply_attempts_attempt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.apply_attempts_attempt_id_seq', 39, true);


--
-- Name: candidate_answers_answer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.candidate_answers_answer_id_seq', 76, true);


--
-- Name: candidate_queries_query_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.candidate_queries_query_id_seq', 1, true);


--
-- Name: candidate_rankings_ranking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.candidate_rankings_ranking_id_seq', 95, true);


--
-- Name: candidates_candidate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.candidates_candidate_id_seq', 42, true);


--
-- Name: company_info_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.company_info_info_id_seq', 1, true);


--
-- Name: email_codes_code_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.email_codes_code_id_seq', 23, true);


--
-- Name: interviews_interview_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interviews_interview_id_seq', 18, true);


--
-- Name: job_questions_question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.job_questions_question_id_seq', 44, true);


--
-- Name: jobs_job_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.jobs_job_id_seq', 25, true);


--
-- Name: notifications_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_notification_id_seq', 44, true);


--
-- Name: offers_offer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.offers_offer_id_seq', 7, true);


--
-- Name: password_resets_reset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.password_resets_reset_id_seq', 1, false);


--
-- Name: role_invites_invite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.role_invites_invite_id_seq', 1, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 22, true);


--
-- Name: apply_attempts apply_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apply_attempts
    ADD CONSTRAINT apply_attempts_pkey PRIMARY KEY (attempt_id);


--
-- Name: candidate_answers candidate_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_answers
    ADD CONSTRAINT candidate_answers_pkey PRIMARY KEY (answer_id);


--
-- Name: candidate_queries candidate_queries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_queries
    ADD CONSTRAINT candidate_queries_pkey PRIMARY KEY (query_id);


--
-- Name: candidate_rankings candidate_rankings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_rankings
    ADD CONSTRAINT candidate_rankings_pkey PRIMARY KEY (ranking_id);


--
-- Name: candidates candidates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT candidates_pkey PRIMARY KEY (candidate_id);


--
-- Name: company_info company_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_info
    ADD CONSTRAINT company_info_pkey PRIMARY KEY (info_id);


--
-- Name: email_codes email_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_codes
    ADD CONSTRAINT email_codes_pkey PRIMARY KEY (code_id);


--
-- Name: interviews interviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_pkey PRIMARY KEY (interview_id);


--
-- Name: job_questions job_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_questions
    ADD CONSTRAINT job_questions_pkey PRIMARY KEY (question_id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (job_id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (notification_id);


--
-- Name: offers offers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.offers
    ADD CONSTRAINT offers_pkey PRIMARY KEY (offer_id);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (reset_id);


--
-- Name: role_invites role_invites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_invites
    ADD CONSTRAINT role_invites_pkey PRIMARY KEY (invite_id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (token);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: idx_apply_attempts_ip_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_apply_attempts_ip_time ON public.apply_attempts USING btree (ip_address, created_at);


--
-- Name: uq_candidates_email_job; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_candidates_email_job ON public.candidates USING btree (lower(email), job_id) WHERE (user_id IS NULL);


--
-- Name: candidate_answers candidate_answers_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_answers
    ADD CONSTRAINT candidate_answers_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(candidate_id) ON DELETE CASCADE;


--
-- Name: candidate_answers candidate_answers_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_answers
    ADD CONSTRAINT candidate_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.job_questions(question_id);


--
-- Name: candidate_queries candidate_queries_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_queries
    ADD CONSTRAINT candidate_queries_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(candidate_id) ON DELETE CASCADE;


--
-- Name: candidates candidates_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT candidates_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(job_id);


--
-- Name: candidates candidates_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT candidates_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: company_info company_info_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_info
    ADD CONSTRAINT company_info_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(user_id);


--
-- Name: interviews interviews_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(candidate_id);


--
-- Name: job_questions job_questions_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_questions
    ADD CONSTRAINT job_questions_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(job_id) ON DELETE CASCADE;


--
-- Name: jobs jobs_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(user_id);


--
-- Name: jobs jobs_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- Name: notifications notifications_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(job_id) ON DELETE CASCADE;


--
-- Name: notifications notifications_to_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_to_user_id_fkey FOREIGN KEY (to_user_id) REFERENCES public.users(user_id);


--
-- Name: offers offers_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.offers
    ADD CONSTRAINT offers_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(candidate_id);


--
-- Name: role_invites role_invites_invited_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_invites
    ADD CONSTRAINT role_invites_invited_by_fkey FOREIGN KEY (invited_by) REFERENCES public.users(user_id);


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 6uCod2mrrF9f495JhFhe8h7Qa82cRPQ1Z08AcEa2Kw5uPMo0AaFAzrek2HuJmTG

