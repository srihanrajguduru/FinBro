# FinBro 💰

Gamified personal finance platform — save smarter, crush debt, earn FBT token rewards.

FinBro is a modern, premium web application designed to help users take control of their personal finances. Users can track transactions, simulate complex debt payoff plans using Avalanche or Snowball methods, forecast retirement savings using compound interest, complete interactive financial literacy quizzes, and earn native ERC-20 FinBroTokens (FBT) as achievements.

---

## Features

- **Comprehensive Dashboard**: View total income, expenses, savings rate, savings targets, and category-by-category expense breakdowns.
- **Smart Transactions & Budget Limits**: Automatically enforces savings targets (20% for professionals, 15% for students) and triggers spending warnings (at 80% and 95% of student limits).
- **Interactive Debt Payoff Simulator**: Compare month-by-month repayment timelines and total interest differences between the **Debt Avalanche** and **Debt Snowball** strategies.
- **Retirement Forecasting**: Run compound interest projections based on current savings, monthly contributions, and estimated annual return rates.
- **FinBroToken (FBT) Rewards**: Gamified reward mechanism that mints ERC-20 FBT tokens on-chain (or in mock Web3 mode) upon completing savings goals.
- **AI Financial Assistant**: Conversational assistant powered by Gemini AI (`gemini-3.1-flash`) providing prompt, personalized financial guidance and platform tips.
- **Push Notification Center**: System alerts for limit warnings, goal completions, and on-chain reward transaction logs.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16 (App Router), React 19, Tailwind CSS v4, Lucide Icons, Recharts, Zustand (State Management), TanStack Query v5 |
| **Backend** | FastAPI, SQLAlchemy 2 (Async), PostgreSQL (via asyncpg), Alembic (Migrations), JWT Authentication, passlib (Argon2 Hashing) |
| **Web3** | Solidity, Web3.js (mock Web3 client fallback mode enabled by default) |

---

## Folder Structure

```text
FinBro/
├── .github/
│   └── workflows/
│       └── ci.yml             # Github Actions Continuous Integration
├── server/                    # Python Backend
│   ├── alembic/               # Alembic Migrations
│   ├── app/
│   │   ├── api/               # API Router Handlers
│   │   ├── core/              # DB, Auth, Config Initialization
│   │   ├── models/            # SQLAlchemy Database Models
│   │   ├── services/          # Pure Business Logic & Calculations
│   │   └── main.py            # FastAPI Entry Point
│   ├── tests/                 # Backend Unit Tests
│   ├── pyproject.toml         # Ruff/Linter Configuration
│   ├── requirements.txt       # Dependencies
│   └── Dockerfile             # Container configuration
└── web/                       # Next.js Frontend
    ├── app/                   # App Router Pages & Layouts
    ├── components/            # React Components & UI primitives
    ├── lib/                   # API client, Stores, Utilities
    ├── eslint.config.mjs      # ESLint Configuration
    ├── package.json           # Dependencies & Scripts
    └── Dockerfile             # Frontend Container configuration
```

---

## Architecture Overview

The application utilizes a classic client-server decoupled architecture:

```mermaid
graph TD
    Client[Next.js Frontend] -->|HTTP / JSON / JWT| API[FastAPI API Gateway]
    API -->|Router| Controllers[API Routers]
    Controllers -->|Invoke| Services[Business Logic Services]
    Services -->|Query| DB[(PostgreSQL Database)]
    Services -->|Transact| Web3[Sepolia Smart Contract / Mock Web3]
```

1. **Frontend**: Manages user interface, application state via Zustand, and data caching using TanStack Query.
2. **Backend**: Performs token authentication, input validation via Pydantic, and coordinates transactions.
3. **Services Layer**: Isolates financial formulas and rules (e.g. debt repayment ordering, interest compounding, reward minting) from the database layer.
4. **Database**: PostgreSQL holds transactions, goals, debts, users, and notifications, mapped cleanly with SQLAlchemy.

---

## Screenshots

*Placeholders for user-provided screenshots:*

### Home Page
`[Screenshot: Home Page Mockup]`

### Login
`[Screenshot: Login Interface]`

### Dashboard
`[Screenshot: Dashboard Charts and Metrics]`

### Transactions
`[Screenshot: Transaction Ledger]`

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 22+
- Docker (for PostgreSQL database)

### 1. Database Setup
Start PostgreSQL on port `5432` using Docker:
```bash
docker compose up postgres -d
```

### 2. Backend Installation
```bash
cd server
pip install -r requirements.txt email-validator
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Installation
```bash
cd ../web
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment Variables

### Backend (`server/.env`)
```env
DATABASE_URL=postgresql+asyncpg://finbro:finbro@localhost:5432/finbro
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
WEB3_RPC_URL=
WEB3_PRIVATE_KEY=
FBT_CONTRACT_ADDRESS=
SEPOLIA_CHAIN_ID=11155111
MOCK_WEB3=true
```

### Frontend (`web/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running the Project

### Development
- **Backend**: `uvicorn app.main:app --reload --port 8000` (from `server/`)
- **Frontend**: `npm run dev` (from `web/`)

### Production Build (Frontend)
```bash
cd web
npm run build
npm run start
```

### Testing
- **Backend**: `pytest` (from `server/`)
- **Frontend Lints & Typechecks**: `npm run lint && npm run typecheck` (from `web/`)

---

## API Documentation

### Authentication
- `POST /auth/register`: Create a new account.
- `POST /auth/login`: Authenticate and get JWT token pair.
- `POST /auth/demo`: Instantiate and log in as the static Demo account.
- `GET /auth/me`: Get current user details.

### Debt Simulator
- `POST /debts/payoff/simulate`: Run Avalanche/Snowball repayment comparison.
  - **Request**: `{"strategy": "avalanche", "extra_payment": 200}`
  - **Response**: Returns months to payoff, total interest paid, and monthly amortization table.

### Predictions
- `POST /predict/retirement`: Calculate future savings balance.
  - **Request**: `{"current_age": 25, "retirement_age": 65, "current_savings": 10000, "monthly_contribution": 500, "annual_return_rate": 7.0}`

---

## Database Schema

```mermaid
erDiagram
    users ||--o{ transactions : has
    users ||--o{ goals : sets
    users ||--o{ debts : owes
    users ||--o{ retirement_projections : projects
    users ||--o{ reward_transactions : earns
    users ||--o{ notifications : receives

    users {
        string id PK
        string email
        string hashed_password
        string full_name
        string user_type
        float monthly_salary
        float monthly_spending_limit
        boolean onboarding_complete
        float fbt_balance
    }
```

---

## Future Improvements

- **Interactive Financial Advisor**: Upgrade intent-matching chat to a retrieval-augmented generation (RAG) assistant.
- **On-chain Integrations**: Enable gasless transactions (EIP-2612) and wallet connect profiles for direct ERC-20 token withdrawals.
- **Bank Feeds Integration**: Sync user accounts via Plaid to automatically pull real-time banking transactions.

---

## Contributing

We welcome contributions to FinBro! Please follow these guidelines:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Ensure all linter checks and tests pass (`ruff check .`, `pytest`, `npm run lint`).
4. Commit your changes and submit a pull request.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Author

Created by **Srihan Raj Guduru** - [@srihanrajguduru](https://github.com/srihanrajguduru)
