# Overview

SkillBridge Africa is a professional networking platform that connects skilled professionals with clients across Africa. The platform enables users to create profiles as either Professionals (offering services) or Clients (seeking services), with features for messaging, reviews, payments, and subscription-based premium plans. Built with Flask, PostgreSQL, and modern web technologies, the application emphasizes a pan-African professional aesthetic with green and earth-tone branding.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Flask Framework**: Web application built with Flask using factory pattern with `create_app()` function
- **SQLAlchemy ORM**: Database abstraction with custom Base class using DeclarativeBase
- **Blueprint Organization**: Modular structure with separate blueprints for admin, auth, billing, messaging, profiles, public, and reviews
- **Database Models**: Comprehensive enum-based data modeling for user roles, profile types, payment status, and subscription management
- **Service Layer**: Dedicated services for email (SMTP), M-Pesa payments, and profanity filtering

## Frontend Architecture
- **Template Engine**: Jinja2 templating with component-based architecture
- **CSS Framework**: TailwindCSS via CDN with custom pan-African color palette (greens, earth tones, gold accents)
- **JavaScript**: Vanilla JavaScript with modular organization for ratings, profanity filtering, and UI interactions
- **Responsive Design**: Mobile-first approach with Tailwind utility classes
- **Component System**: Reusable template components for profile cards, reviews, star ratings, and loaders

## Authentication & Authorization
- **Flask-Login**: Session-based user authentication with UserMixin
- **Role-Based Access**: Two-tier system with USER and ADMIN roles
- **Email Verification**: OTP-based email verification using Flask-Mail
- **Admin Authentication**: Separate admin panel with password-protected access and session management

## Data Architecture
- **Multi-Profile System**: Users can create up to 5 profiles (mix of Client/Professional types)
- **Location Hierarchy**: Structured location data with Country/County/Sub-County/Town fields
- **Subscription Management**: Plan-based premium features with M-Pesa payment integration
- **Review System**: Multi-dimensional rating system (professionalism, skill, ease of work)
- **Message System**: 1:1 messaging with profanity filtering and admin broadcast capabilities

## Payment Integration
- **M-Pesa Integration**: Kenya mobile money payment processing with sandbox/live environment support
- **Subscription Plans**: Tiered pricing with audience-specific plans (Client vs Professional)
- **Payment Tracking**: Comprehensive payment history and status monitoring

## Content Management
- **Admin Panel**: Full CMS capabilities for user management, content updates, and platform settings
- **Media Management**: Configurable photo/video upload system with pluggable storage interface
- **Homepage Management**: Dynamic homepage photos and announcement system
- **Profanity Filtering**: Multi-language profanity detection (English, Swahili) with real-time validation

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework with SQLAlchemy, Login, and Mail extensions
- **PostgreSQL**: Primary database with connection pooling and environment-based configuration
- **SQLAlchemy**: ORM with Alembic migrations support
- **Werkzeug**: WSGI utilities including ProxyFix middleware for production deployment

## Frontend Dependencies
- **TailwindCSS**: Styling framework loaded via CDN
- **Font Awesome**: Icon library for UI elements
- **Vanilla JavaScript**: No heavy frontend frameworks, uses modern ES6+ features

## Communication Services
- **Gmail SMTP**: Email service for OTP verification and notifications
- **M-Pesa API**: Safaricom mobile payment integration with consumer key/secret authentication

## Development & Deployment
- **Environment Variables**: Configuration through environment variables for security and deployment flexibility
- **File Upload System**: Local filesystem storage with abstraction layer for future S3/Cloudinary integration
- **Session Management**: Flask sessions with configurable secret keys

## Geographic Data
- **Kenya Location Data**: Hardcoded county and sub-county data for location filtering and profile organization