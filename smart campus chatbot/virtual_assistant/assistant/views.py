from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import random
import datetime
import sympy as sp
import re
import logging
from urllib.parse import quote
from typing import Optional

logger = logging.getLogger(__name__)

class Chatbot:
    """
    College enquiry chatbot with multi-feature support.
    """

    MAX_INPUT_LENGTH = 200

    COURSE_DATA = {
        'cse': {
            'name': 'Computer Science Engineering',
            'duration': '4 years',
            'fees': '$15,000/year',
            'specializations': ['AI', 'Cloud Computing', 'IoT'],
            'website': '/cse'
        },
        'ece': {
            'name': 'Electronics and Communication Engineering',
            'duration': '4 years',
            'fees': '$14,500/year',
            'specializations': ['VLSI', 'Embedded Systems'],
            'website': '/ece'
        },
    }

    RESPONSE_TEMPLATES = {
        "greetings": {
            "hello": "Hello! Welcome to {college_name}. How can I assist you today?",
            "hi": "Hi there! How can I help you with {college_name} information?",
        },
        "college_info": {
            "principal": "Our Principal is {principal_name}",
            "admission": (
                "📋 Admission Process:\n"
                "1. Online Application\n"
                "2. Entrance Exam\n"
                "3. Personal Interview\n"
                "4. Document Verification"
            ),
            "contact": (
                "📞 Contact Us:\n"
                "Phone: {phone}\n"
                "Email: {email}\n"
                "Address: {address}"
            ),
        }
    }

    # Lowercased keys for consistent matching
    PROFESSORS = {
        "kareemulla sir": {
            "name": "Dr. Mohamed Kareemulla",
            "department": "Computer Science",
            "qualification": "PhD",
            "experience": "28 years",
            "email": "kareemulla@drttit.edu.in",
            "research": "Machine Learning, Neural Networks"
        },
        "kharmega sir": {
            "name": "Dr. G. Kharmega Sundararaj",
            "department": "Computer Science",
            "qualification": "PhD",
            "experience": "24 years",
            "email": "drkharmegam@drttit.edu.in",
            "research": "Smart Grids, Renewable Energy"
        },
    }

    JOKES = [
        "Why don't scientists trust atoms? They make up everything!",
        "What do you call fake spaghetti? An impasta!",
    ]

    def __init__(self):
        self.college_name = "ABC College"
        self.principal_name = "Dr. Syed Ariff"
        self.contact_info = {
            'phone': '+1-234-567-890',
            'email': 'info@abccollege.edu',
            'address': '123 College Street, Education City'
        }

    def format_response(self, user_input: str) -> Optional[str]:
        """Respond to exact keyword matches."""
        for category, responses in self.RESPONSE_TEMPLATES.items():
            for keyword, template in responses.items():
                if keyword in user_input:
                    return template.format(
                        college_name=self.college_name,
                        principal_name=self.principal_name,
                        **self.contact_info
                    )
        return None

    def get_professor_details(self, query: str) -> str:
        """Search professor by name with fuzzy matching."""
        query = query.lower()

        for prof_id, prof in self.PROFESSORS.items():
            if prof_id in query:
                return self._format_professor_response(prof)

        for prof_id, prof in self.PROFESSORS.items():
            if any(word in query for word in prof_id.split()):
                return self._format_professor_response(prof)

        return self._list_all_professors()

    def _format_professor_response(self, prof: dict) -> str:
        return (
            f"👨‍🏫 Professor Details:\n"
            f"Name: {prof['name']}\n"
            f"Department: {prof['department']}\n"
            f"Qualification: {prof['qualification']}\n"
            f"Experience: {prof['experience']}\n"
            f"Research Areas: {prof['research']}\n"
            f"Email: {prof['email']}"
        )

    def _list_all_professors(self) -> str:
        prof_list = "\n".join(
            f"- {prof['name']} ({prof['department']})"
            for prof in self.PROFESSORS.values()
        )
        return (
            f"📚 Professors at {self.college_name}:\n{prof_list}\n\n"
            "You can ask for details about a specific professor."
        )

    def get_course_details(self, query: str) -> str:
        query = query.lower()
        for key, course in self.COURSE_DATA.items():
            if key in query or course['name'].lower() in query:
                return (
                    f"📘 {course['name']}:\n"
                    f"Duration: {course['duration']}\n"
                    f"Fees: {course['fees']}\n"
                    f"Specializations: {', '.join(course['specializations'])}\n"
                    f"More Info: {course['website']}"
                )
        return (
            "📚 Available Courses:\n" +
            "\n".join(f"- {c['name']}" for c in self.COURSE_DATA.values())
        )

    def solve_math_problem(self, query: str) -> str:
        try:
            expression = sp.sympify(query)
            result = expression.evalf()
            return f"🧮 Solution: {query.strip()} = {result}"
        except Exception:
            return "❌ I couldn't understand the math problem. Please try again."

    def get_current_time(self) -> str:
        now = datetime.datetime.now()
        return f"📅 Current Date & Time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    def tell_joke(self) -> str:
        return f"😂 {random.choice(self.JOKES)}"

    def search_web(self, query: str) -> str:
        return f"🔍 Here's what I found: https://www.google.com/search?q={quote(query)}"

    def handle_query(self, user_input: str) -> str:
        user_input = user_input.lower().strip()

        if not user_input:
            return "❗ Please type a question."

        exact_response = self.format_response(user_input)
        if exact_response:
            return exact_response

        patterns = {
            r'\b(?:search|find)\b': self.search_web,
            r'\b(?:time|date)\b': lambda _: self.get_current_time(),
            r'\b(?:joke|funny)\b': lambda _: self.tell_joke(),
            r'\b(?:course|program)\b': self.get_course_details,
            r'\b(?:professor|faculty|lecturer|teacher)\b': self.get_professor_details,
            r'(?:[\d\+\-\*/\^\(\)\s]+|solve|calculate)': self.solve_math_problem,
        }

        for pattern, handler in patterns.items():
            if re.search(pattern, user_input):
                query = re.sub(pattern, '', user_input).strip()
                return handler(query) if query else "Please specify your query."

        return (
            "🤖 I can help you with:\n"
            "- 🎓 Course Information\n"
            "- 🧑‍🏫 Professor Details\n"
            "- 🧮 Math Problems\n"
            "- 📅 Date & Time\n"
            "- 📞 Contact Info\n"
            "- 😂 Jokes\n"
            "Just ask me anything!"
        )

@require_GET
def get_response(request):
    user_input = request.GET.get('message', '').strip()

    if not user_input:
        return JsonResponse({'response': "❗ Please enter a message."})

    if len(user_input) > Chatbot.MAX_INPUT_LENGTH:
        return JsonResponse({'response': f"⚠️ Message exceeds {Chatbot.MAX_INPUT_LENGTH} characters."})

    try:
        bot = Chatbot()
        response = bot.handle_query(user_input)
        return JsonResponse({'response': response})
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JsonResponse({'response': "⚠️ An error occurred. Please try again."})

def home(request):
    return render(request, 'index.html', {
        'current_year': datetime.datetime.now().year,
        'college_name': "ABC College"
    })

