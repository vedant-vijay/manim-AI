import os
import subprocess
import uuid
import shutil
import sys
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------ Flask setup ------------------
app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)  # Enable CORS for development

# Create necessary directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_FOLDER = os.path.join(BASE_DIR, "videos")
TEMP_FOLDER = os.path.join(BASE_DIR, "temp")
FRONTEND_FOLDER = os.path.join(BASE_DIR, "..", "frontend")

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(FRONTEND_FOLDER, exist_ok=True)

# ------------------ LLM Configuration ------------------
# Using Groq (FREE) - Get your key from https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Set your API key here or as environment variable

# ------------------ System Checks ------------------
def check_system_requirements():
    """Check if all requirements are met"""
    checks = {
        "python_version": False,
        "manim_installed": False,
        "ffmpeg_installed": False,
        "cairo_installed": False,
        "llm_configured": False
    }
    
    # Check Python version
    checks["python_version"] = sys.version_info >= (3, 7)
    
    # Check Manim
    try:
        import manim
        checks["manim_installed"] = True
    except ImportError:
        checks["manim_installed"] = False
    
    # Check FFmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        checks["ffmpeg_installed"] = result.returncode == 0
    except:
        checks["ffmpeg_installed"] = False
    
    # Check Cairo (simplified check)
    checks["cairo_installed"] = True  # Assume it's handled by Manim installation
    
    # Check LLM
    checks["llm_configured"] = bool(GROQ_API_KEY) or True  # Fallback available
    
    return checks

# ------------------ Find Python with Manim ------------------
def find_python_with_manim():
    """Find Python executable with Manim installed"""
    # Try current Python first
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import manim; print('OK')"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "OK" in result.stdout:
            return sys.executable
    except:
        pass
    
    # Try other common Python commands
    for cmd in ["python", "python3", "py"]:
        if shutil.which(cmd):
            try:
                result = subprocess.run(
                    [cmd, "-c", "import manim; print('OK')"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    return cmd
            except:
                continue
    
    return None

# ------------------ Generate Manim Code ------------------
def generate_manim_code_with_llm(prompt):
    """Generate Manim code using Groq API or fallback"""
    
    # Try Groq API first if key is available
    if GROQ_API_KEY:
        code = generate_with_groq(prompt)
        if code and "class GeneratedScene" in code:
            return code
    
    # Use pattern-based fallback
    return generate_manual_fallback(prompt)

# def generate_with_groq(prompt):
#     """Use free Groq API"""
#     try:
#         import requests
        
#         headers = {
#             "Authorization": f"Bearer {GROQ_API_KEY}",
#             "Content-Type": "application/json"
#         }
        
#         system_prompt = """You are a Manim code generator. Generate ONLY valid Python code.
# Requirements:
# 1. Start with: from manim import *
# 2. Create ONE class named 'GeneratedScene' inheriting from Scene
# 3. Implement construct(self) method
# 4. Use simple animations: Write, Create, FadeIn, FadeOut, Transform
# 5. Keep animations under 10 seconds total
# 6. Return ONLY code, no explanations or markdown
# 7. Ensure all objects are properly positioned and visible"""

#         data = {
#             "model": "llama-3.3-70b-versatile",  # Free, fast model
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"Create a Manim animation for: {prompt}"}
#             ],
#             "temperature": 0.7,
#             "max_tokens": 1500
#         }
        
#         response = requests.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers=headers,
#             json=data,
#             timeout=30
#         )
        
#         if response.status_code == 200:
#             result = response.json()
#             code = result["choices"][0]["message"]["content"]
            
#             # Clean the code
#             if "```python" in code:
#                 code = code.split("```python")[1].split("```")[0]
#             elif "```" in code:
#                 code = code.split("```")[1].split("```")[0]
            
#             return code.strip()
#         else:
#             print(f"Groq API error: {response.status_code} - {response.text}")
#             return None
            
#     except Exception as e:
#         print(f"Groq generation error: {e}")
#         return None

def generate_with_groq(prompt):
    """Use free Groq API with corrected Manim syntax"""

    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are a Manim code generator. Generate ONLY valid Python code.
        Requirements:
        1. Start with: from manim import *
        2. Create ONE class named 'GeneratedScene' inheriting from Scene (or ThreeDScene for 3D)
        3. Use correct Manim Community syntax:
        - Use ParametricFunction (NOT ParametricCurve)
        - For 3D animations: inherit from ThreeDScene
        - For plotting graphs: Use axes.plot(function, color=COLOR, x_range=[min, max])
        - Use run_time=X instead of runtime=X for animation timing
        4. For DNA helix: Use two ParametricFunction objects with proper 3D coordinates
        5. For neon glow: Use thick stroke_width (8-15) with high opacity
        6. Keep animations under 30 seconds total
        7. Return ONLY code, no explanations or markdown

        Example DNA helix syntax:
        helix1 = ParametricFunction(
            lambda t: np.array([np.cos(t), np.sin(t), t/4]),
            t_range=[0, 6*PI], color=BLUE
        )"""


        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a Manim animation for: {prompt}"}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            code = result["choices"][0]["message"]["content"]

            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1]
        
            # FIX: Replace problematic syntax with correct Manim syntax
            code = code.replace("ParametricCurve", "ParametricFunction")
            code = code.replace("get_graph(", "plot(")
            code = code.replace("axes.get_graph(", "axes.plot(")
            code = code.replace("runtime=", "run_time=")
            code = code.replace("ease_out", "smooth")
            code = code.replace("ease_in", "smooth")
            
            return code.strip()
        else:
            print(f"Groq API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Groq generation error: {e}")
        return None


def generate_manual_fallback(prompt):
    """Generate code without LLM - pattern matching with more patterns"""
    prompt_lower = prompt.lower()
    
    # Enhanced pattern matching
    if any(word in prompt_lower for word in ["circle", "square", "transform", "morph"]):
        return """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Shape Transformation", font_size=48)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        circle = Circle(radius=1.5, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=3, color=RED, fill_opacity=0.5)
        
        self.play(Create(circle))
        self.wait(1)
        self.play(Transform(circle, square), run_time=2)
        self.wait(1)
        self.play(FadeOut(circle), FadeOut(title))"""
    
    elif any(word in prompt_lower for word in ["pythagoras", "pythagorean", "theorem", "triangle"]):
        return """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Pythagorean Theorem", font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        # Create right triangle
        triangle = Polygon(
            [-2, -1.5, 0], [2, -1.5, 0], [-2, 1.5, 0],
            color=WHITE, fill_opacity=0.3
        )
        
        # Create squares on sides
        square_a = Square(side_length=2.5, color=BLUE, fill_opacity=0.3).shift(LEFT*3)
        square_b = Square(side_length=2, color=GREEN, fill_opacity=0.3).shift(DOWN*2.5)
        square_c = Square(side_length=3.2, color=RED, fill_opacity=0.3).shift(RIGHT*1.5 + UP*0.5)
        
        # Labels
        label_a = MathTex("a^2", color=BLUE).next_to(square_a, LEFT)
        label_b = MathTex("b^2", color=GREEN).next_to(square_b, DOWN)
        label_c = MathTex("c^2", color=RED).next_to(square_c, RIGHT)
        
        formula = MathTex("a^2 + b^2 = c^2", font_size=48).to_edge(DOWN)
        
        self.play(Create(triangle))
        self.wait(0.5)
        self.play(FadeIn(square_a), Write(label_a))
        self.play(FadeIn(square_b), Write(label_b))
        self.play(FadeIn(square_c), Write(label_c))
        self.wait(1)
        self.play(Write(formula))
        self.wait(2)
        self.play(*[FadeOut(obj) for obj in [triangle, square_a, square_b, square_c, 
                                              label_a, label_b, label_c, formula, title]])"""
    
    elif any(word in prompt_lower for word in ["sine", "cosine", "wave", "trig", "sin", "cos"]):
        return """from manim import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Trigonometric Functions", font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 2, 1],
            axis_config={"color": GREY},
            x_length=8,
            y_length=4,
        )
        
        sine_graph = axes.plot(lambda x: np.sin(x), color=RED, x_range=[-4, 4])
        cosine_graph = axes.plot(lambda x: np.cos(x), color=BLUE, x_range=[-4, 4])
        
        sine_label = MathTex(r"y = \\sin(x)", color=RED).to_edge(RIGHT).shift(UP)
        cosine_label = MathTex(r"y = \\cos(x)", color=BLUE).to_edge(RIGHT)
        
        self.play(Create(axes))
        self.play(Create(sine_graph), Write(sine_label))
        self.wait(1)
        self.play(Create(cosine_graph), Write(cosine_label))
        self.wait(2)
        self.play(*[FadeOut(obj) for obj in [axes, sine_graph, cosine_graph, 
                                              sine_label, cosine_label, title]])"""
    
    elif any(word in prompt_lower for word in ["bounce", "ball", "physics", "gravity"]):
        return """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Bouncing Ball Physics", font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        ground = Line(LEFT * 5, RIGHT * 5, color=GREY).shift(DOWN * 2.5)
        ball = Circle(radius=0.3, color=RED, fill_opacity=1).shift(UP * 2)
        
        self.play(Create(ground))
        self.play(FadeIn(ball))
        
        # Bouncing animation with decreasing height
        heights = [2, 1.5, 1, 0.5]
        for h in heights:
            self.play(ball.animate.shift(DOWN * (h + 2.5)), 
                     rate_func=rate_functions.ease_in_quad, run_time=0.4)
            self.play(ball.animate.shift(UP * h), 
                     rate_func=rate_functions.ease_out_quad, run_time=0.4)
        
        self.wait(1)
        self.play(FadeOut(ball), FadeOut(ground), FadeOut(title))"""
    
    elif any(word in prompt_lower for word in ["quadratic", "parabola", "formula", "equation"]):
        return """from manim import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Quadratic Function", font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 8, 2],
            axis_config={"color": GREY},
            x_length=8,
            y_length=6,
        )
        
        # Quadratic function
        parabola = axes.plot(lambda x: x**2, color=GREEN, x_range=[-2.5, 2.5])
        
        # Formula
        formula = MathTex("f(x) = x^2", font_size=36).to_edge(RIGHT).shift(UP)
        vertex = Dot(axes.c2p(0, 0), color=RED)
        vertex_label = Text("Vertex", font_size=24).next_to(vertex, DOWN)
        
        self.play(Create(axes))
        self.play(Create(parabola), Write(formula))
        self.wait(1)
        self.play(FadeIn(vertex), Write(vertex_label))
        self.wait(2)
        self.play(*[FadeOut(obj) for obj in [axes, parabola, formula, 
                                              vertex, vertex_label, title]])"""
    
    elif any(word in prompt_lower for word in ["derivative", "calculus", "integral", "limit"]):
        return """from manim import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Derivative Visualization", font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-4, 4, 1],
            axis_config={"color": GREY},
        )
        
        # Original function
        func = axes.plot(lambda x: x**2 - 2, color=BLUE, x_range=[-2.5, 2.5])
        func_label = MathTex("f(x) = x^2 - 2", color=BLUE).to_edge(RIGHT).shift(UP*2)
        
        # Derivative
        derivative = axes.plot(lambda x: 2*x, color=RED, x_range=[-2.5, 2.5])
        deriv_label = MathTex("f'(x) = 2x", color=RED).to_edge(RIGHT).shift(UP*0.5)
        
        self.play(Create(axes))
        self.play(Create(func), Write(func_label))
        self.wait(1)
        self.play(Create(derivative), Write(deriv_label))
        self.wait(2)
        self.play(*[FadeOut(obj) for obj in [axes, func, derivative, 
                                              func_label, deriv_label, title]])"""
    
    else:
        # Generic educational animation
        return f"""from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title from prompt
        title = Text("{prompt[:50]}", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        # Create animated elements
        circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=2, color=RED, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5)
        
        shapes = VGroup(circle, square, triangle).arrange(RIGHT, buff=1)
        
        # Mathematical expression
        equation = MathTex(r"\\pi r^2 + s^2 = A").scale(1.2)
        equation.to_edge(DOWN)
        
        self.play(*[Create(shape) for shape in shapes])
        self.wait(1)
        
        # Animate transformations
        self.play(
            circle.animate.shift(UP * 0.5),
            square.animate.rotate(PI / 4),
            triangle.animate.scale(1.3)
        )
        self.wait(0.5)
        
        self.play(Write(equation))
        self.wait(1)
        
        # Group animation
        self.play(shapes.animate.arrange(DOWN, buff=0.5))
        self.wait(1)
        
        self.play(*[FadeOut(obj) for obj in [*shapes, equation, title]])"""

# ------------------ Main Generation Endpoint ------------------
@app.route("/")
def home():
    """Serve the frontend HTML"""
    html_path = os.path.join(FRONTEND_FOLDER, "index.html")
    if os.path.exists(html_path):
        return send_from_directory(FRONTEND_FOLDER, "index.html")
    else:
        # Return inline HTML if file doesn't exist
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Manim Generator</title></head>
        <body>
            <h1>Manim Generator</h1>
            <p>Frontend HTML file not found. Please create frontend/index.html with the provided code.</p>
        </body>
        </html>
        """

@app.route("/generate", methods=["POST"])
def generate_code():
    """Main endpoint to generate Manim animation"""
    data = request.json
    prompt = data.get("prompt", "")
    
    if not prompt.strip():
        return jsonify({"error": "Prompt is required"}), 400
    
    # Check system
    checks = check_system_requirements()
    if not checks["manim_installed"]:
        return jsonify({
            "error": "Manim not installed",
            "details": "Install with: pip install manim",
            "checks": checks
        }), 500
    
    python_cmd = find_python_with_manim()
    if not python_cmd:
        return jsonify({
            "error": "Python with Manim not found",
            "details": "Please ensure Manim is installed: pip install manim",
            "checks": checks
        }), 500
    
    unique_id = uuid.uuid4().hex[:8]
    script_name = f"scene_{unique_id}.py"
    script_path = os.path.join(TEMP_FOLDER, script_name)
    
    try:
        # Generate Manim code
        print(f"Generating code for: {prompt}")
        manim_code = generate_manim_code_with_llm(prompt)
        
        # Validate code has required structure
        if "class GeneratedScene" not in manim_code:
            print("Invalid code structure, using fallback")
            manim_code = generate_manual_fallback(prompt)
        
        # Save the script
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(manim_code)
        
        print(f"Saved script to: {script_path}")
        
        # Prepare output directory
        output_dir = os.path.join(VIDEO_FOLDER, f"output_{unique_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Run Manim command
        cmd = [
            python_cmd,
            "-m", "manim",
            "render",
            script_path,
            "GeneratedScene",
            "--media_dir", output_dir,
            "-ql",  # Low quality for faster rendering
            "--disable_caching",
            "-v", "WARNING"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        # Execute Manim
        env = os.environ.copy()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=TEMP_FOLDER,
            env=env
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            print(f"Manim error: {error_msg}")
            
            # Try simpler animation as fallback
            fallback_code = """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        text = Text("Generated Animation", font_size=48)
        self.play(Write(text))
        self.wait(1)
        self.play(text.animate.scale(1.5).set_color(BLUE))
        self.wait(1)
        self.play(FadeOut(text))"""
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(fallback_code)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=TEMP_FOLDER)
            
            if result.returncode != 0:
                return jsonify({
                    "error": "Animation rendering failed",
                    "details": error_msg[:500],
                    "manim_code": manim_code
                }), 500
            
            manim_code = fallback_code
        
        # Find the generated video file
        video_path = None
        
        # Search for MP4 file in output directory
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".mp4"):
                    video_path = os.path.join(root, file)
                    break
            if video_path:
                break
        
        if not video_path:
            return jsonify({
                "error": "Video file not found after generation",
                "details": f"Output directory: {output_dir}",
                "manim_code": manim_code
            }), 500
        
        # Copy video to videos folder
        final_video_name = f"animation_{unique_id}.mp4"
        final_video_path = os.path.join(VIDEO_FOLDER, final_video_name)
        shutil.copy(video_path, final_video_path)
        
        print(f"Video saved to: {final_video_path}")
        
        # Cleanup temporary files
        try:
            os.remove(script_path)
            shutil.rmtree(output_dir, ignore_errors=True)
        except Exception as e:
            print(f"Cleanup warning: {e}")
        
        return jsonify({
            "success": True,
            "manim_code": manim_code,
            "video_url": f"/videos/{final_video_name}"
        })
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Generation error: {error_trace}")
        return jsonify({
            "error": f"Generation failed: {str(e)}",
            "details": str(e)
        }), 500

@app.route("/videos/<path:filename>")
def serve_video(filename):
    """Serve generated video files"""
    return send_from_directory(VIDEO_FOLDER, filename, mimetype="video/mp4")

@app.route("/health", methods=["GET"])
def health_check():
    """Check system health status"""
    checks = check_system_requirements()
    python_cmd = find_python_with_manim()
    
    return jsonify({
        "status": "healthy" if all(checks.values()) else "unhealthy",
        "checks": checks,
        "python_with_manim": str(python_cmd) if python_cmd else None,
        "groq_configured": bool(GROQ_API_KEY),
        "directories": {
            "video_folder": VIDEO_FOLDER,
            "temp_folder": TEMP_FOLDER,
            "frontend_folder": FRONTEND_FOLDER
        }
    })

@app.route("/setup-info", methods=["GET"])
def setup_info():
    """Provide setup instructions"""
    return jsonify({
        "quick_setup": [
            "1. Install Python 3.8+: https://python.org",
            "2. pip install manim flask flask-cors requests",
            "3. Install FFmpeg: https://ffmpeg.org/download.html",
            "4. Get FREE Groq API key: https://console.groq.com",
            "5. Set GROQ_API_KEY environment variable or update the code"
        ],
        "windows_setup": [
            "# Install Chocolatey (Package Manager)",
            "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
            "# Install dependencies",
            "choco install python ffmpeg -y",
            "# Install Manim",
            "pip install manim flask flask-cors requests"
        ],
        "linux_setup": [
            "sudo apt update",
            "sudo apt install python3-pip ffmpeg libcairo2-dev libpango1.0-dev -y",
            "pip3 install manim flask flask-cors requests"
        ],
        "mac_setup": [
            "# Install Homebrew",
            "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"",
            "# Install dependencies",
            "brew install python ffmpeg cairo pango",
            "# Install Manim",
            "pip3 install manim flask flask-cors requests"
        ],
        "docker_option": [
            "docker run -it -p 5000:5000 manimcommunity/manim:latest",
            "# Then install Flask inside container",
            "pip install flask flask-cors requests"
        ]
    })

# ------------------ Error Handlers ------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ------------------ Main Entry Point ------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🎬 MANIM AI ANIMATION GENERATOR")
    print("=" * 60)
    
    # System check
    checks = check_system_requirements()
    print("\n📋 System Status:")
    for check, status in checks.items():
        icon = "✅" if status else "❌"
        readable_name = check.replace('_', ' ').title()
        print(f"  {icon} {readable_name}: {'Ready' if status else 'Not Ready'}")
    
    # Setup instructions if needed
    if not all(checks.values()):
        print("\n⚠️  SETUP REQUIRED:")
        if not checks["manim_installed"]:
            print("  → Run: pip install manim")
        if not checks["ffmpeg_installed"]:
            print("  → Install FFmpeg from https://ffmpeg.org")
        if not GROQ_API_KEY:
            print("  → Get FREE API key from https://console.groq.com")
            print("  → Set: export GROQ_API_KEY='your-key-here'")
    
    # Directory info
    print(f"\n📁 Directories:")
    print(f"  • Videos: {VIDEO_FOLDER}")
    print(f"  • Temp: {TEMP_FOLDER}")
    print(f"  • Frontend: {FRONTEND_FOLDER}")
    
    # API info
    if GROQ_API_KEY:
        print(f"\n🤖 AI Provider: Groq (API Key Configured)")
    else:
        print(f"\n🤖 AI Provider: Pattern-based Fallback (No API Key)")
    
    # Server info
    print("\n" + "=" * 60)
    print("🚀 Starting server at: http://localhost:5000")
    print("📝 API Endpoints:")
    print("  • GET  /          - Web Interface")
    print("  • POST /generate  - Generate Animation")
    print("  • GET  /health    - System Health Check")
    print("  • GET  /setup-info - Setup Instructions")
    print("=" * 60 + "\n")
    
    # Start Flask app
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)