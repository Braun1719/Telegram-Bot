# services/test_calculator.py
from typing import Dict, List, Any
from models.questions import MaslachQuestions, BoykoTestQuestions, HeckHessTestQuestions

class TestCalculator:
    """Сервис для расчета результатов тестов для ИТ-специалистов"""
    
    @staticmethod
    def calculate_maslach(answers: Dict[int, int]) -> Dict[str, Any]:
        """Расчет результатов опросника Маслач для ИТ"""
        scores = {"EE": 0, "DP": 0, "PA": 0}
        
        for q_id, answer in answers.items():
            question = MaslachQuestions.get_question(q_id)
            if question.reversed:
                adjusted_answer = 6 - answer  # Шкала от 1 до 5
            else:
                adjusted_answer = answer
            scores[question.scale] += adjusted_answer
        
        # Нормировка баллов для ИТ
        ee_level = TestCalculator._interpret_ee_score(scores["EE"])
        dp_level = TestCalculator._interpret_dp_score(scores["DP"])
        pa_level = TestCalculator._interpret_pa_score(scores["PA"])
        
        overall = TestCalculator._get_overall_level(ee_level, dp_level, pa_level)
        
        return {
            'scores': scores,
            'interpretation': {
                'EE': {'score': scores["EE"], 'level': ee_level},
                'DP': {'score': scores["DP"], 'level': dp_level},
                'PA': {'score': scores["PA"], 'level': pa_level},
                'overall': overall
            },
            'it_specific': True
        }
    
    @staticmethod
    def _interpret_ee_score(score: int) -> str:
        if score < 12: return "низкий"
        elif score < 19: return "средний"
        else: return "высокий"
    
    @staticmethod
    def _interpret_dp_score(score: int) -> str:
        if score < 5: return "низкий"
        elif score < 10: return "средний"
        else: return "высокий"
    
    @staticmethod
    def _interpret_pa_score(score: int) -> str:
        if score > 25: return "низкий"
        elif score > 18: return "средний"
        else: return "высокий"
    
    @staticmethod
    def _get_overall_level(ee: str, dp: str, pa: str) -> str:
        if ee == "высокий" and dp == "высокий":
            return "критический уровень выгорания в ИТ"
        elif ee == "высокий" or dp == "высокий":
            return "повышенный риск выгорания"
        return "нормальный уровень, риски минимальны"
    
    @staticmethod
    def calculate_boyko_test(answers: Dict[int, str]) -> Dict[str, Any]:
        """Расчет результатов теста Бойко для ИТ-специалистов"""
        
        # Инициализируем словари для всех фаз
        phases_scores = {"фаза1": 0, "фаза2": 0, "фаза3": 0, "фаза4": 0}
        phase_questions_count = BoykoTestQuestions.get_questions_count_by_phase()
        
        for q_id, answer in answers.items():
            try:
                question = BoykoTestQuestions.get_question(q_id)
                phase = question.scale
                
                # Подсчет баллов с учетом специфики ИТ
                if answer == "yes":
                    phases_scores[phase] += 2  # Да = 2 балла
                elif answer == "sometimes":
                    phases_scores[phase] += 1  # Иногда = 1 балл
                # Нет = 0 баллов
                    
            except Exception as e:
                print(f"Ошибка при обработке вопроса {q_id}: {e}")
                continue
        
        # Процентное соотношение по фазам
        percentages = {}
        max_possible_scores = {phase: count * 2 for phase, count in phase_questions_count.items()}
        
        for phase in phases_scores:
            max_score = max_possible_scores.get(phase, 1)
            if max_score > 0:
                percentage = (phases_scores[phase] / max_score) * 100
                percentages[phase] = round(percentage, 1)
            else:
                percentages[phase] = 0
        
        # Определение доминирующей фазы
        dominant_phase = max(percentages, key=percentages.get) if percentages else "фаза1"
        
        # Оценка уровня выгорания по доминирующей фазе
        phase_levels = {}
        for phase, percentage in percentages.items():
            if percentage < 25:
                phase_levels[phase] = {"level": "низкий", "emoji": "🟢"}
            elif percentage < 50:
                phase_levels[phase] = {"level": "умеренный", "emoji": "🟡"}
            elif percentage < 75:
                phase_levels[phase] = {"level": "высокий", "emoji": "🟠"}
            else:
                phase_levels[phase] = {"level": "критический", "emoji": "🔴"}
        
        # Общая оценка (средний процент по всем фазам)
        active_phases = [p for p in percentages.values() if p > 0]
        if active_phases:
            total_percentage = sum(active_phases) / len(active_phases)
        else:
            total_percentage = 0
        
        # Определение общего уровня выгорания для ИТ-специалиста
        if total_percentage < 25:
            overall = "Низкий уровень выгорания. Вы хорошо справляетесь с рабочими нагрузками."
            color = "🟢"
            risk = "низкий"
        elif total_percentage < 50:
            overall = "Умеренный уровень выгорания. Рекомендуется профилактика."
            color = "🟡"
            risk = "умеренный"
        elif total_percentage < 75:
            overall = "Высокий уровень выгорания. Требуется вмешательство и изменения в рабочем процессе."
            color = "🟠"
            risk = "высокий"
        else:
            overall = "Критический уровень выгорания. Необходимы срочные меры и возможен перерыв в работе."
            color = "🔴"
            risk = "критический"
        
        # Фаза-индикатор (самая проблемная)
        indicator_phase = max(percentages.items(), key=lambda x: x[1])[0] if percentages else "фаза1"
        
        return {
            'phases': phases_scores,
            'phase_questions_count': phase_questions_count,
            'percentages': percentages,
            'phase_levels': phase_levels,
            'dominant_phase': dominant_phase,
            'indicator_phase': indicator_phase,
            'total_percentage': round(total_percentage, 1),
            'overall': overall,
            'color': color,
            'risk_level': risk,
            'max_possible_scores': max_possible_scores,
            'is_it_specific': True,
            'recommendation_focus': indicator_phase
        }
    
    @staticmethod
    def calculate_heck_hess_test(answers: Dict[int, int]) -> Dict[str, Any]:
        """Расчет результатов теста Хека-Хесса для ИТ-специалистов"""
        
        # Инициализация счетчиков по шкалам
        scales = {
            'depression': 0,
            'burnout': 0,
            'anxiety': 0
        }
        
        # Подсчет баллов по шкалам (ответы от 0 до 3)
        for q_id, answer in answers.items():
            question = HeckHessTestQuestions.get_question(q_id)
            if question.scale in scales:
                scales[question.scale] += answer
        
        # Общий балл
        total_score = sum(scales.values())
        
        # Интерпретация по общему баллу
        if total_score <= 7:
            overall_level, interpretation = "норма", "Отсутствие значимых признаков депрессии"
            color = "🟢"
        elif total_score <= 12:
            overall_level, interpretation = "субдепрессия", "Легкие депрессивные симптомы"
            color = "🟡"
        elif total_score <= 18:
            overall_level, interpretation = "умеренная депрессия", "Средняя выраженность симптомов"
            color = "🟠"
        elif total_score <= 24:
            overall_level, interpretation = "выраженная депрессия", "Требуется консультация специалиста"
            color = "🔴"
        else:
            overall_level, interpretation = "тяжелая депрессия", "Необходима срочная помощь"
            color = "🔴"
        
        # Анализ по шкалам
        scale_results = {}
        scoring_info = HeckHessTestQuestions.get_scoring_info()
        
        for scale, score in scales.items():
            info = scoring_info.get(scale, {})
            # Определение уровня для каждой шкалы
            if score <= info.get('low', [0, 0, ""])[1]:
                level, level_description = "низкий", info.get('low', [0, 0, ""])[2]
            elif score <= info.get('moderate', [0, 0, ""])[1]:
                level, level_description = "умеренный", info.get('moderate', [0, 0, ""])[2]
            elif score <= info.get('high', [0, 0, ""])[1]:
                level, level_description = "высокий", info.get('high', [0, 0, ""])[2]
            else:
                level, level_description = "критический", info.get('severe', [0, 0, ""])[2]
            
            scale_results[scale] = {
                'score': score,
                'level': level,
                'description': level_description,
                'max_score': 36 if scale == 'depression' else 32 if scale == 'burnout' else 34
            }
        
        # Оценка риска выгорания для ИТ
        burnout_risk = "низкий"
        if scale_results['burnout']['score'] > 16:
            burnout_risk = "повышенный"
        if scale_results['burnout']['score'] > 24:
            burnout_risk = "высокий"
        if scale_results['burnout']['score'] > 32:
            burnout_risk = "критический"
        
        # Рекомендации для ИТ-специалистов
        recommendations = []
        if scale_results['burnout']['level'] in ['высокий', 'критический']:
            recommendations.append("• Рекомендуется сократить рабочие часы и взять перерыв")
            recommendations.append("• Обратиться к психологу или коучу")
            recommendations.append("• Обсудить нагрузку с руководителем")
        if scale_results['depression']['level'] in ['высокий', 'критический']:
            recommendations.append("• Консультация психотерапевта рекомендуется")
            recommendations.append("• Рассмотреть вариант отпуска или саббатикала")
        if scale_results['anxiety']['level'] in ['высокий', 'критический']:
            recommendations.append("• Техники релаксации и mindfulness могут помочь")
            recommendations.append("• Практиковать медитацию для снижения тревожности")
        
        return {
            'total_score': total_score,
            'overall_level': overall_level,
            'interpretation': interpretation,
            'color': color,
            'scales': scale_results,
            'burnout_risk': burnout_risk,
            'recommendations': recommendations,
            'thresholds': {
                'норма': (0, 7),
                'субдепрессия': (8, 12),
                'умеренная депрессия': (13, 18),
                'выраженная депрессия': (19, 24),
                'тяжелая депрессия': (25, 63)
            },
            'max_total_score': 63,
            'questions_count': len(HeckHessTestQuestions.get_all()),
            'it_specific': True
        }
    
    @staticmethod
    def calculate_quick_test(answers: List[int]) -> Dict[str, Any]:
        """Расчет результатов быстрого теста для ИТ"""
        total = sum(answers)
        
        if total <= 10:
            level, risk, color = "низкий", "Низкий риск выгорания в ИТ", "🟢"
        elif total <= 20:
            level, risk, color = "умеренный", "Средний риск, рекомендуется профилактика", "🟡"
        elif total <= 30:
            level, risk, color = "высокий", "Высокий риск, требуются изменения", "🟠"
        else:
            level, risk, color = "критический", "Критический риск, срочные меры", "🔴"
        
        # Рекомендации для ИТ
        recommendations = []
        if total > 20:
            recommendations.append("• Установите границы рабочего времени")
            recommendations.append("• Делайте регулярные перерывы от экрана")
            recommendations.append("• Практикуйте техники релаксации")
        if total > 30:
            recommendations.append("• Рассмотрите возможность отпуска")
            recommendations.append("• Обратитесь к специалисту")
            recommendations.append("• Обсудите нагрузку с руководством")
        
        return {
            'scores': {
                'total': total,
                'max': 40,
                'level': level,
                'risk': risk,
                'color': color
            },
            'interpretation': {
                'score': total,
                'level': level,
                'recommendation': risk
            },
            'recommendations': recommendations,
            'it_specific': True
        }