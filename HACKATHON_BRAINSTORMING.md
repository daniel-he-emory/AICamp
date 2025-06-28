# 🚀 Hackathon Brainstorming & Task Assignment

## 📋 Team Information
- **Team Name**: SmartBites
- **Event**: [Hackathon Name]
- **Date**: [Event Date]
- **Duration**: [Event Duration]

---

## 💡 Project Ideas Brainstorming

### Idea 1: NutriMCP – Personalized Meal Planner with Auto-Grocery Purchasing

**Description**:  
A web app that designs personalized meal plans based on user demographics, dietary needs, and medical conditions (e.g., diabetes, hypertension), and automatically purchases the necessary groceries via grocery store MCP (Multi-Channel Platform) APIs.

**Problem Solved**:  
Helps users eat healthier while saving time by automating both planning and shopping. Solves friction between health advice and execution.

**Target Audience**:  
- Health-conscious individuals  
- People with chronic conditions (e.g., diabetes, allergies)  
- Busy professionals  
- Elderly users or caregivers  

**Tech Stack**:  
- Frontend: React + Tailwind CSS  
- Backend: FastAPI (Python)  
- Database: PostgreSQL + Redis  
- APIs/Services: OpenAI, USDA FoodData Central, Instacart/Walmart MCP, Stripe  

**Features**:  
- [ ] Personalized meal plan generator (AI-based)  
- [ ] Nutrition + allergen checker  
- [ ] One-click grocery cart integration (via MCP)  

**Pros**:  
- Automates entire “plan → shop” journey  
- Addresses health and accessibility use cases  

**Cons**:  
- Need to integrate several 3rd party APIs  
- Need dietary logic that is medically accurate  

---

### Idea 2: FitFuel – Meal Planning for Fitness Enthusiasts

**Description**:  
Meal planner that generates weekly meal prep recipes aligned to fitness goals (e.g., muscle gain, fat loss), including calorie and macro tracking.

**Problem Solved**:  
Removes guesswork from meal planning for gym-goers.

**Target Audience**:  
Fitness enthusiasts, athletes, personal trainers  

**Tech Stack**:  
- Frontend: Vue.js  
- Backend: Node.js + Express  
- Database: MongoDB  
- APIs/Services: FitnessPal API, USDA API  

**Features**:  
- [ ] Goal-based recipe generation  
- [ ] Macro calculator  
- [ ] Grocery list export  

**Pros**:  
- Narrow and focused  
- Fast implementation  

**Cons**:  
- Limited market outside fitness  
- Doesn’t integrate shopping directly  

---

### Idea 3: CareMeal – Senior Meal Companion

**Description**:  
Tool for caregivers of elderly patients to plan safe, tasty, easy-to-chew meals that comply with medication and health conditions.

**Problem Solved**:  
Improves caregiving by reducing food-related health incidents  

**Target Audience**:  
Elderly people, caregivers, family  

**Tech Stack**:  
- Frontend: Svelte  
- Backend: Flask  
- Database: Firebase  
- APIs/Services: Medications + diet restriction lookup  

**Features**:  
- [ ] Elder-friendly recipe generator  
- [ ] Warning system for ingredient-med conflicts  
- [ ] Caregiver dashboard  

**Pros**:  
- Impactful socially  
- Targets underserved market  

**Cons**:  
- Requires domain expertise  
- Lower generalizability  

---

## 🎯 Final Project Decision

**Selected Project**: NutriMCP – Personalized Meal Planner with Auto-Grocery Purchasing  

**Why this project?**:  
- Combines personalization + automation + e-commerce  
- Broad consumer use case  
- Potential for real-world adoption  

**MVP Features**:  
- [ ] AI-powered meal plan from user profile  
- [ ] Ingredient extraction and grocery list generation  
- [ ] MCP API integration to place grocery order  

**Stretch Goals** (if time permits):  
- [ ] Dynamic substitution (if item is out of stock)  
- [ ] Real-time nutrition tracking with wearable integration  

---

## 👥 Team Roles & Responsibilities

### Team Member 1: Alex  
**Role**: Backend Developer  
**Skills**: Python, FastAPI, API integration  
**Responsibilities**:  
- [ ] Build meal plan API  
- [ ] Integrate grocery MCP  
- [ ] User profile management  

### Team Member 2: Jamie  
**Role**: Frontend Developer  
**Skills**: React, Tailwind, UX design  
**Responsibilities**:  
- [ ] Build user profile form  
- [ ] Display meal plans and grocery carts  
- [ ] Link to checkout  

### Team Member 3: Sam  
**Role**: Data & AI Engineer  
**Skills**: GPT API, NLP, food dataset parsing  
**Responsibilities**:  
- [ ] Meal generation prompt tuning  
- [ ] Nutrition fact extraction  
- [ ] Food allergen/diet checks  

### Team Member 4: Casey  
**Role**: Project Manager & QA  
**Skills**: Product planning, testing, coordination  
**Responsibilities**:  
- [ ] Task assignment  
- [ ] Testing flows  
- [ ] Presentation & demo  

---

## 📅 Project Timeline

### Phase 1: Planning & Setup (Hour 0-2)  
- [x] Finalize project idea  
- [x] Set up development environment  
- [x] Create project repository  
- [x] Set up basic project structure  
- [x] Assign initial tasks  

### Phase 2: Core Development (Hour 2-8)  
- [ ] Backend: meal plan API  
- [ ] Frontend: user profile + result page  
- [ ] Database setup for users and preferences  
- [ ] Grocery API endpoint integration  

### Phase 3: Features & Polish (Hour 8-12)  
- [ ] UI polish and styling  
- [ ] Add dietary warnings  
- [ ] Testing flows  

### Phase 4: Final Touches (Hour 12-14)  
- [ ] README and walkthrough  
- [ ] Live demo prep  
- [ ] Team pitch practice  

---

## 🛠️ Technical Decisions

### Architecture  
- **Frontend Framework**: React  
- **Backend Framework**: FastAPI  
- **Database**: PostgreSQL  
- **Deployment**: Render / Vercel  

### APIs & Services  
- [ ] OpenAI API: meal planning  
- [ ] USDA FoodData API: nutrition  
- [ ] Instacart / Walmart MCP: grocery purchasing  

### Development Tools  
- **Version Control**: Git + GitHub  
- **IDE/Editor**: VS Code  
- **Communication**: Discord  
- **Project Management**: Trello  

---

## 📝 Notes & Ideas

### Random Ideas  
- Idea 1: Add wearable integration for calorie intake  
- Idea 2: Budget-friendly grocery constraints  
- Idea 3: Family planning mode  

### Resources & References  
- [USDA API](https://fdc.nal.usda.gov/api-key-signup.html)  
- [Instacart Developer API](https://www.instacart.com/company/developers)  
- [OpenAI GPT](https://platform.openai.com/)  

### Challenges & Solutions  
**Challenge 1**: Accurate mapping from meals to grocery items  
- **Solution**: Use NLP and tagging library (e.g., Spoonacular)  

**Challenge 2**: Multiple diet restrictions  
- **Solution**: Create a rule engine to filter recipes  

---

## ✅ Daily Check-ins

### Day 1 Progress  
**What was accomplished?**:  
- Backend scaffold  
- Initial meal planner working  
- MCP API key request sent  

**What are the blockers?**:  
- Grocery item standardization  
- Limited free credits on API  

**Next steps**:  
- Connect frontend to backend  
- Build shopping cart flow  

### Day 2 Progress  
**What was accomplished?**:  
- Full meal → grocery flow completed  
- UI design near final  

**What are the blockers?**:  
- Deployment issues  
- Missing test users  

**Next steps**:  
- Run user test  
- Polish demo  

---

## 🎉 Final Submission Checklist

### Code  
- [x] All code is committed and pushed  
- [x] Repository is public/accessible  
- [x] README.md is complete  
- [ ] Code is well-documented  

### Demo  
- [x] Demo is prepared  
- [x] All features work as expected  
- [ ] Presentation slides are ready  
- [ ] Team members know their parts  

### Documentation  
- [x] Project description is clear  
- [ ] Installation instructions are provided  
- [ ] API documentation (if applicable)  
- [x] Screenshots/videos of the application  

---

## 💬 Team Communication

### Meeting Schedule  
- **Daily Standup**: 9:00 AM  
- **Progress Review**: 2:00 PM  
- **Final Prep**: 6:00 PM  

### Communication Channels  
- **Slack/Discord**: #smartbites-team  
- **GitHub**: https://github.com/smartbites/hackathon2025  
- **Other**: Notion  

---

*Last Updated: 2025-06-28*  
*Next Review: 2025-06-29*
