from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict
import random
import os
import time

# ====================== Вспомогательные функции для красоты ======================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_slow(text: str, delay: float = 0.03):
    """Печатает текст посимвольно для эффекта чата."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_header(title: str):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def print_success(msg: str):
    print(f"✅ {msg}")

def print_error(msg: str):
    print(f"❌ {msg}")

def print_info(msg: str):
    print(f"ℹ️  {msg}")

def print_wait():
    input("\nНажмите Enter, чтобы продолжить...")

# ====================== Базовые классы предметной области ======================

class Profile:
    def __init__(self, user_id: int, name: str, email: str):
        self.userId = user_id
        self.name = name
        self.email = email
        self.registrationDate = datetime.now()

class Word:
    def __init__(self, word_id: int = 0, word: str = "", translation: str = "", pinyin: str = ""):
        self.id = word_id
        self.word = word
        self.translation = translation
        self.pinyin = pinyin
        self.examples = []

    def __repr__(self):
        return f"{self.word} ({self.pinyin}) — {self.translation}"

class Task(ABC):
    def __init__(self, task_id: int = 0, difficulty: str = "EASY"):
        self.id = task_id
        self.difficulty = difficulty
        self.content = ""
        self.answer = ""
        self.hint = ""

    @abstractmethod
    def checkAnswer(self, answer: str) -> bool:
        pass

    def get_difficulty_stars(self) -> str:
        if self.difficulty == "EASY":
            return "★☆☆"
        elif self.difficulty == "MEDIUM":
            return "★★☆"
        else:
            return "★★★"

class DialogueTask(Task):
    def __init__(self, task_id: int = 0, difficulty: str = "EASY"):
        super().__init__(task_id, difficulty)
        self.dialogueLines = []

    def checkAnswer(self, answer: str) -> bool:
        return answer.strip().lower() == self.answer.strip().lower()

class WordTask(Task):
    def __init__(self, task_id: int = 0, difficulty: str = "EASY", word: Optional[Word] = None):
        super().__init__(task_id, difficulty)
        self.word = word if word else Word()

    def checkAnswer(self, answer: str) -> bool:
        return answer.strip().lower() == self.word.translation.lower()

# ====================== Паттерн Наблюдатель (Observer) ======================

class Observer(ABC):
    @abstractmethod
    def update(self, progress: 'UserProgress'):
        pass

class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer):
        pass

    @abstractmethod
    def detach(self, observer: Observer):
        pass

    @abstractmethod
    def notify(self):
        pass

class UserProgress(Subject):
    def __init__(self):
        self._observers: List[Observer] = []
        self.completedAt: Optional[datetime] = None
        self.score: int = 0
        self.task: Optional[Task] = None
        self.total_tasks_completed = 0
        self.total_score = 0

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def complete_task(self, task: Task, score: int):
        self.completedAt = datetime.now()
        self.score = score
        self.task = task
        self.total_tasks_completed += 1
        self.total_score += score
        self.notify()

class AchievementManager(Observer):
    def __init__(self):
        self.achievements = []

    def update(self, progress: UserProgress):
        if progress.score == 100 and "Идеально" not in self.achievements:
            self.achievements.append("Идеально")
            print_slow("🏆  ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО: 'Идеальное выполнение'! (100 очков)")
        if progress.total_tasks_completed == 5 and "Новичок" not in self.achievements:
            self.achievements.append("Новичок")
            print_slow("🏆  ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО: 'Новичок' (5 заданий выполнено)")
        if progress.total_score >= 300 and "Знаток" not in self.achievements:
            self.achievements.append("Знаток")
            print_slow("🏆  ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО: 'Знаток' (300+ очков)")

class AnalyticsService(Observer):
    def update(self, progress: UserProgress):
        # Можно сохранять в файл, но для консоли выведем кратко
        pass

class UINotifier(Observer):
    def update(self, progress: UserProgress):
        print(f"📊  Всего заданий: {progress.total_tasks_completed} | Общий счёт: {progress.total_score}")

# ====================== Паттерн Декоратор (Decorator) ======================

class TaskDecorator(Task):
    _task: Task

    def __init__(self, task: Task):
        self._task = task

    @property
    def id(self):
        return self._task.id

    @property
    def difficulty(self):
        return self._task.difficulty

    @property
    def content(self):
        return self._task.content

    @property
    def answer(self):
        return self._task.answer

    def checkAnswer(self, answer: str) -> bool:
        return self._task.checkAnswer(answer)

class TimedTaskDecorator(TaskDecorator):
    def __init__(self, task: Task, time_limit_seconds: int):
        super().__init__(task)
        self._start_time: Optional[datetime] = None
        self._time_limit = time_limit_seconds

    def start_timer(self):
        self._start_time = datetime.now()
        print(f"⏱️  У вас {self._time_limit} секунд на ответ!")

    def checkAnswer(self, answer: str) -> bool:
        if self._start_time is None:
            self.start_timer()  # автоматически запускаем, если забыли
        elapsed = (datetime.now() - self._start_time).seconds
        if elapsed > self._time_limit:
            print("⌛ Время вышло!")
            return False
        return self._task.checkAnswer(answer)

class HintedTaskDecorator(TaskDecorator):
    def __init__(self, task: Task, hint: str):
        super().__init__(task)
        self.hint_text = hint

    def show_hint(self):
        print(f"💡 Подсказка: {self.hint_text}")

# ====================== Паттерн Абстрактная фабрика (Abstract Factory) ======================

class TaskFactory(ABC):
    @abstractmethod
    def create_dialogue_task(self) -> DialogueTask:
        pass

    @abstractmethod
    def create_word_task(self) -> WordTask:
        pass

class EasyTaskFactory(TaskFactory):
    def create_dialogue_task(self) -> DialogueTask:
        task = DialogueTask(difficulty="EASY")
        task.dialogueLines = ["你好！", "你叫什么名字？"]
        task.content = "Вопрос: 你叫什么名字？\nКак ответить 'Меня зовут Ли Мин'?"
        task.answer = "我叫李明"
        task.hint = "Используйте 叫 (jiào) для имени."
        return task

    def create_word_task(self) -> WordTask:
        word = Word(word="猫", translation="кошка", pinyin="māo")
        task = WordTask(difficulty="EASY", word=word)
        task.content = f"Переведите слово: {word.word} (пиньинь: {word.pinyin})"
        task.answer = "кошка"
        task.hint = "Домашнее животное, которое ловит мышей."
        return task

class HardTaskFactory(TaskFactory):
    def create_dialogue_task(self) -> DialogueTask:
        task = DialogueTask(difficulty="HARD")
        task.dialogueLines = ["请问，去故宫怎么走？", "一直往前走，然后右转。"]
        task.content = "Диалог: 请问，去故宫怎么走？\nОтветьте по-китайски: 'Идите прямо, затем поверните направо.'"
        task.answer = "一直往前走然后右转"
        task.hint = "一直 (yīzhí) — прямо; 右转 (yòuzhuǎn) — повернуть направо."
        return task

    def create_word_task(self) -> WordTask:
        word = Word(word="尴尬", translation="неловкий", pinyin="gāngà")
        task = WordTask(difficulty="HARD", word=word)
        task.content = f"Переведите слово: {word.word} (пиньинь: {word.pinyin})"
        task.answer = "неловкий"
        task.hint = "Ситуация, когда вам стыдно или неудобно."
        return task

# ====================== Паттерн Фабричный метод (Factory Method) ======================

class User(ABC):
    def __init__(self, user_id: int, name: str, email: str, password_hash: str):
        self.id = user_id
        self.name = name
        self.email = email
        self.passwordHash = password_hash

    @abstractmethod
    def login(self, credentials) -> bool:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    def viewProfile(self) -> Profile:
        return Profile(self.id, self.name, self.email)

class RegisteredUser(User):
    def __init__(self, user_id: int, name: str, email: str, password_hash: str):
        super().__init__(user_id, name, email, password_hash)
        self.progress = UserProgress()
        self.progress.attach(AchievementManager())
        self.progress.attach(UINotifier())
        self.progress_list: List[UserProgress] = []
        self.current_factory = EasyTaskFactory()  # по умолчанию лёгкий уровень

    def login(self, credentials) -> bool:
        return True

    def logout(self) -> None:
        print_slow(f"{self.name}, вы вышли из системы.")

    # ---------- Фабричный метод ----------
    def generateNewTask(self) -> Task:
        return self._create_task()

    def _create_task(self) -> Task:
        """По умолчанию случайное задание."""
        if random.choice([True, False]):
            return self.current_factory.create_dialogue_task()
        else:
            return self.current_factory.create_word_task()
    # ---------------------------------------

    def chooseDifficulty(self, level: str):
        if level.upper() == "EASY":
            self.current_factory = EasyTaskFactory()
            print_success("Уровень сложности: ЛЁГКИЙ")
        elif level.upper() == "HARD":
            self.current_factory = HardTaskFactory()
            print_success("Уровень сложности: СЛОЖНЫЙ")
        else:
            print_error("Неизвестный уровень, остаётся прежний.")

    def practiceDialogue(self):
        """Интерактивное выполнение одного задания."""
        task = self.generateNewTask()
        # Применяем декораторы
        timed_task = TimedTaskDecorator(task, time_limit_seconds=30)
        hinted_task = HintedTaskDecorator(timed_task, task.hint)

        print_header(f"ЗАДАНИЕ ({task.get_difficulty_stars()})")
        print_slow(task.content)
        print()

        # Возможность запросить подсказку
        while True:
            answer = input("Ваш ответ (или введите '?' для подсказки): ").strip()
            if answer == '?':
                hinted_task.show_hint()
                continue
            break

        is_correct = hinted_task.checkAnswer(answer)
        if is_correct:
            print_success("Правильно! Отличная работа!")
            score = 100
        else:
            print_error(f"Неправильно. Правильный ответ: {task.answer}")
            score = 50

        self.progress.complete_task(task, score)
        return is_correct

    def learnNewWords(self) -> List[Word]:
        return [Word(word="书", translation="книга", pinyin="shū"),
                Word(word="电脑", translation="компьютер", pinyin="diànnǎo")]

class ChildUser(RegisteredUser):
    def _create_task(self) -> Task:
        word = Word(word="狗", translation="собака", pinyin="gǒu")
        task = WordTask(difficulty="EASY", word=word)
        task.content = f"Как переводится '{word.word}' ({word.pinyin})?"
        task.answer = "собака"
        task.hint = "Друг человека."
        return task

class AdvancedUser(RegisteredUser):
    def _create_task(self) -> Task:
        task = DialogueTask(difficulty="HARD")
        task.dialogueLines = ["你今天感觉怎么样？", "我有点累，但是还好。"]
        task.content = "Ответьте по-китайски: 'Я немного устал, но всё в порядке.'"
        task.answer = "我有点累但是还好"
        task.hint = "有点 (yǒudiǎn) — немного; 累 (lèi) — усталый."
        return task

class Administrator(User):
    def login(self, credentials) -> bool:
        return True

    def logout(self) -> None:
        print("Администратор вышел.")

    def viewAllUsers(self) -> List[User]:
        return []

    def manageUser(self, user_id: int):
        print(f"Управление пользователем ID {user_id}")

class Guest(User):
    def login(self, credentials) -> bool:
        return False

    def logout(self) -> None:
        pass

    def register(self, data) -> RegisteredUser:
        new_user = RegisteredUser(user_id=random.randint(1000,9999),
                                  name=data['name'],
                                  email=data['email'],
                                  password_hash="hash")
        print_slow(f"🎉 Регистрация прошла успешно! Добро пожаловать, {new_user.name}!")
        return new_user

# ====================== ИНТЕРАКТИВНОЕ МЕНЮ ======================

def run_chatbot():
    clear_screen()
    print_header("КИТАЙСКИЙ ЧАТ-БОТ ДЛЯ ТРЕНИРОВКИ ЯЗЫКА")
    print_slow("Здравствуйте! Я помогу вам практиковать китайский язык.\n")

    current_user: Optional[RegisteredUser] = None

    while True:
        if current_user is None:
            # Меню для неавторизованного пользователя
            print("\n1. Войти как гость (регистрация)")
            print("2. Войти как администратор (демо)")
            print("3. Выйти из программы")
            choice = input("\nВыберите действие: ").strip()

            if choice == '1':
                name = input("Введите ваше имя: ").strip()
                email = input("Введите email: ").strip()
                guest = Guest(0, "Гость", "guest@test.com", "")
                current_user = guest.register({"name": name, "email": email})
                print_wait()
                clear_screen()
            elif choice == '2':
                current_user = Administrator(999, "Admin", "admin@bot.com", "")
                print_slow("Вы вошли как администратор (режим просмотра).")
                print_info("Доступен просмотр пользователей, но обучение недоступно.")
                print_wait()
                clear_screen()
                # После просмотра выходим обратно
                current_user = None
            elif choice == '3':
                print_slow("再见！ (До свидания!)")
                break
            else:
                print_error("Неверный ввод.")
        else:
            # Меню для зарегистрированного пользователя
            print_header(f"ПРОФИЛЬ: {current_user.name} | Очки: {current_user.progress.total_score}")
            print("\n1. Тренироваться (выполнить задание)")
            print("2. Сменить уровень сложности")
            print("3. Посмотреть выученные слова")
            print("4. Просмотреть профиль")
            print("5. Выйти из аккаунта")
            print("6. Выйти из программы")

            choice = input("\nВыберите действие: ").strip()

            if choice == '1':
                clear_screen()
                current_user.practiceDialogue()
                print_wait()
                clear_screen()
            elif choice == '2':
                level = input("Введите уровень (EASY / HARD): ").strip().upper()
                current_user.chooseDifficulty(level)
                print_wait()
                clear_screen()
            elif choice == '3':
                clear_screen()
                print_header("ИЗУЧЕННЫЕ СЛОВА")
                words = current_user.learnNewWords()
                for w in words:
                    print(f"• {w}")
                print_wait()
                clear_screen()
            elif choice == '4':
                clear_screen()
                profile = current_user.viewProfile()
                print_header("ПРОФИЛЬ")
                print(f"ID: {profile.userId}")
                print(f"Имя: {profile.name}")
                print(f"Email: {profile.email}")
                print(f"Дата регистрации: {profile.registrationDate.strftime('%Y-%m-%d %H:%M')}")
                print(f"Выполнено заданий: {current_user.progress.total_tasks_completed}")
                print(f"Общий счёт: {current_user.progress.total_score}")
                print_wait()
                clear_screen()
            elif choice == '5':
                current_user.logout()
                current_user = None
                print_wait()
                clear_screen()
            elif choice == '6':
                print_slow("再见！ (До свидания!)")
                break
            else:
                print_error("Неверный ввод.")
                print_wait()
                clear_screen()

if __name__ == "__main__":
    run_chatbot()