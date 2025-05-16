# Project Neptune

A comprehensive project management and KPI tracking system built with Python and Flask.

## Features

- Project management and tracking
- KPI (Key Performance Indicator) monitoring
- Real-time data visualization
- User role-based access control
- Interactive dashboards
- Automated reporting

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Project-Neptune.git
cd Project-Neptune
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:

```bash
flask db upgrade
```

6. Run the application:

```bash
flask run
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
