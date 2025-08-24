# FinSentinel
An intelligent financial guardian that continuously monitors your Investment portfolio . Built with AWS automation, it fetches data periodically, compares values against user-defined thresholds, and stores information when conditions are met. A chatbot interface provides instant insights and advice, making it a watchtower for your investments.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Features and Functionality](#features-and-functionality)
5. [API Endpoints](#api-endpoints)
6. [Database Schema](#database-schema)
7. [Security Implementation](#security-implementation)
8. [Frontend Components](#frontend-components)
9. [Backend Services](#backend-services)
10. [Deployment Architecture](#deployment-architecture)
11. [Monitoring and Alerts](#monitoring-and-alerts)
12. [Performance Considerations](#performance-considerations)
13. [Future Enhancements](#future-enhancements)

---

## Project Overview

The Stock Price Tracking System is a comprehensive cloud-based application that enables users to monitor stock prices and receive alerts when stocks fall below specified threshold values. The system provides real-time stock monitoring, portfolio management, and intelligent alerting capabilities through a modern web interface.

### Key Objectives
- **Portfolio Management**: Allow users to add, remove, and track multiple stocks
- **Price Monitoring**: Continuously monitor stock prices using external APIs
- **Alert System**: Generate alerts when stocks breach user-defined thresholds
- **Data Visualization**: Provide intuitive charts and graphs for portfolio insights
- **Security**: Implement robust authentication and data encryption

---

## System Architecture

The application follows a serverless, microservices architecture deployed on AWS cloud infrastructure:

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Frontend      │    │ API Gateway  │    │ Lambda Functions│
│   (S3 Bucket)   │◄──►│              │◄──►│                 │
│   HTML/CSS/JS   │    │              │    │ - Add Stock     │
└─────────────────┘    └──────────────┘    │ - Delete Stock  │
                                           │ - View Stocks   │
                                           │ - Alert Handler │
                                           └─────────────────┘
                              │                       │
                              ▼                       ▼
                    ┌──────────────┐        ┌─────────────────┐
                    │  DynamoDB    │        │ External APIs   │
                    │  Database    │        │ (Stock Prices)  │
                    └──────────────┘        └─────────────────┘
```

---

## Technology Stack

### Frontend
- **HTML5**: Structure and semantic markup
- **CSS3 & Tailwind CSS**: Responsive styling and modern UI components
- **JavaScript (ES6+)**: Dynamic functionality and API interactions
- **Chart.js**: Data visualization for portfolio analytics

### Backend
- **AWS Lambda**: Serverless compute for business logic
- **Python 3.9**: Lambda function runtime
- **AWS API Gateway**: RESTful API management and routing
- **AWS DynamoDB**: NoSQL database for data storage
- **AWS S3**: Static website hosting

### External Integrations
- **Stock Price APIs**: Real-time market data retrieval
- **LiveChat AI**: Integrated financial chatbot assistance

---

## Features and Functionality

### Core Features

#### 1. Stock Portfolio Management
- **Add Stocks**: Search and add stocks using FIGI identifiers
- **Remove Stocks**: Delete stocks from tracking portfolio
- **View Portfolio**: Display all tracked stocks with current data
- **Stock Search**: Intelligent search with autocomplete functionality

#### 2. Price Monitoring System
- **Real-time Updates**: Automated price fetching every hour
- **Threshold Monitoring**: Continuous comparison against user-defined limits
- **Alert Generation**: Automatic alert creation when thresholds are breached
- **Historical Tracking**: Maintain records of all price movements and alerts

#### 3. Data Visualization
- **Portfolio Pie Chart**: Visual representation of stock distribution
- **Price Trend Lines**: Historical price movement analysis
- **Alert Dashboard**: Comprehensive view of all generated alerts

#### 4. Security Features
- **Password Encryption**: Caesar cipher implementation for data protection
- **User Authentication**: Email and password-based access control
- **CORS Security**: Restricted cross-origin access policies

---

## API Endpoints

### Base URL
```
https://ich68whaml.execute-api.ap-south-1.amazonaws.com/prd
```

### Endpoint Specifications

#### 1. Add Stock (`POST /create-row`)
**Purpose**: Add a new stock to user's portfolio

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "userpassword",
    "figi": "BBG000CZ0677",
    "display_symbol": "AAPL",
    "price": 150.00
}
```

**Response**:
```json
{
    "message": "Stock added successfully"
}
```

#### 2. Delete Stock (`POST /delete-row`)
**Purpose**: Remove a stock from user's portfolio

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "userpassword",
    "figi": "BBG000CZ0677"
}
```

#### 3. View Portfolio (`POST /get-the-by-email`)
**Purpose**: Retrieve all stocks for a user

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "userpassword"
}
```

**Response**:
```json
{
    "message": "Data retrieved successfully",
    "data": [
        {
            "email": "user@example.com",
            "figi": "BBG000CZ0677",
            "display_symbol": "AAPL",
            "price": 150.00
        }
    ]
}
```

#### 4. View Alerts (`POST /alert_show`)
**Purpose**: Display all alerts for user's stocks

**Request Body**: Same as portfolio view
**Response**: Array of alert records with timestamps

---

## Database Schema

### Primary Table: `PRICE_TRACKER_DB`

#### Stock Records
```
Partition Key: email (String)
Sort Key: figi (String)

Attributes:
- email: User email address
- figi: Financial Instrument Global Identifier
- display_symbol: Stock ticker symbol
- price: Threshold price (Decimal)
- password: Encrypted user password
```

#### Alert Records
```
Partition Key: email (String)
Sort Key: alert_id (String)

Attributes:
- email: User email address
- figi: Stock identifier
- display_symbol: Stock symbol
- current_price: Price when alert triggered
- threshold_price: User-defined threshold
- timestamp: Alert generation time
- alert_type: Type of alert (below_threshold)
```

---

## Security Implementation

### Encryption Strategy
**Caesar Cipher Implementation**:
- Passwords encrypted using a shift cipher (default shift: 3)
- Both alphabetic and numeric characters transformed
- Maintains original character case and special symbols

```python
def caesar_encrypt(text: str, shift: int = 3) -> str:
    result = ''
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        elif char.isdigit():
            result += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        else:
            result += char
    return result
```

### CORS Configuration
- Restricted to specific S3 bucket origin
- Controlled HTTP methods and headers
- Credential-based access control

---

## Frontend Components

### User Interface Design
- **Responsive Layout**: Tailwind CSS for mobile-first design
- **Component-Based Architecture**: Modular sections for different functionalities
- **Interactive Elements**: Real-time search, form validation, and dynamic charts

### Key JavaScript Modules

#### 1. Stock Search System
- Debounced search with 300ms delay
- Keyboard navigation support (Arrow keys, Enter, Escape)
- Real-time filtering from 50,000+ stock dataset

#### 2. Chart Rendering
- Dynamic pie charts for portfolio distribution
- Line charts for price trend analysis
- Responsive design with Chart.js library

#### 3. API Communication
- Centralized API calling function with error handling
- CORS-compliant request formatting
- Secure credential management

---

## Backend Services

### Lambda Function Architecture

#### 1. Create Stock Function
- **Validation**: Input sanitization and required field verification
- **Business Logic**: Duplicate checking and user existence validation
- **Database Operations**: Item creation and updates in DynamoDB

#### 2. Delete Stock Function
- **Authentication**: Password verification against encrypted storage
- **Deletion Logic**: Safe removal with existence checking
- **Error Handling**: Comprehensive error responses

#### 3. Data Retrieval Functions
- **Query Optimization**: Efficient DynamoDB scan operations
- **Data Filtering**: Password-based access control
- **Response Formatting**: JSON serialization with Decimal handling

#### 4. Price Monitoring Service
- **Scheduled Execution**: Hourly price updates via CloudWatch Events
- **External API Integration**: Real-time stock price fetching
- **Alert Logic**: Threshold comparison and alert generation

---

## Deployment Architecture

### AWS Services Configuration

#### 1. S3 Bucket Setup
- **Static Website Hosting**: Enabled for frontend delivery
- **Public Access**: Configured for web accessibility
- **CORS Policy**: Aligned with API Gateway settings

#### 2. API Gateway Configuration
- **REST API**: RESTful endpoint management
- **Stage Management**: Production stage deployment
- **Rate Limiting**: Request throttling for resource protection

#### 3. DynamoDB Configuration
- **On-Demand Billing**: Cost-effective scaling model
- **Global Secondary Indexes**: Optimized query performance
- **Backup Strategy**: Point-in-time recovery enabled

#### 4. Lambda Deployment
- **Runtime**: Python 3.9 with optimized memory allocation
- **Environment Variables**: Secure configuration management
- **IAM Roles**: Least privilege access principles

---

## Monitoring and Alerts

### System Monitoring
- **CloudWatch Metrics**: Lambda function performance tracking
- **Error Logging**: Comprehensive error capture and analysis
- **API Gateway Monitoring**: Request/response metrics and latency tracking

### Alert Mechanisms
- **Threshold Alerts**: Automated generation when stocks breach limits
- **System Alerts**: Infrastructure health monitoring
- **User Notifications**: Email-based alert delivery system

---

## Performance Considerations

### Optimization Strategies

#### Frontend Optimization
- **Lazy Loading**: Deferred chart rendering for improved initial load times
- **Debounced Search**: Reduced API calls through intelligent search timing
- **Caching Strategy**: Local storage of frequently accessed stock data

#### Backend Optimization
- **Connection Pooling**: Efficient DynamoDB connection management
- **Batch Operations**: Bulk processing for price updates
- **Memory Optimization**: Right-sized Lambda functions for cost efficiency

#### Database Optimization
- **Query Patterns**: Optimized access patterns for DynamoDB
- **Index Strategy**: Strategic use of Global Secondary Indexes
- **Data Modeling**: Efficient partition and sort key design

---

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Technical indicator calculations and trend analysis
2. **Mobile Application**: Native iOS and Android applications
3. **Real-time WebSocket**: Live price streaming for immediate updates
4. **Machine Learning**: Predictive analytics for stock price movements
5. **Social Features**: Portfolio sharing and community insights
6. **Advanced Security**: Multi-factor authentication and OAuth integration

### Scalability Improvements
1. **Microservices Decomposition**: Further service breakdown for specific functions
2. **Caching Layer**: Redis/ElastiCache for improved response times
3. **CDN Integration**: CloudFront for global content delivery
4. **Multi-Region Deployment**: Geographic distribution for reduced latency

---

## Technical Specifications

### System Requirements
- **Browser Compatibility**: Modern browsers with ES6 support
- **Network Requirements**: Stable internet connection for real-time updates
- **Device Support**: Desktop and mobile responsive design

### Performance Metrics
- **Response Time**: <500ms for API calls
- **Availability**: 99.9% uptime target
- **Scalability**: Support for 10,000+ concurrent users
- **Data Accuracy**: Real-time price updates within 1-hour intervals

---

## Conclusion

The Stock Price Tracking System represents a comprehensive, cloud-native solution for portfolio management and stock monitoring. Built on AWS serverless architecture, it provides scalable, secure, and cost-effective stock tracking capabilities with modern web technologies and intelligent alerting mechanisms.

The system's modular design and robust security features make it suitable for both individual investors and small financial institutions seeking reliable stock monitoring solutions.
