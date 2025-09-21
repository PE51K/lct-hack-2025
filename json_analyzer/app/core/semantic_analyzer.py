import re
from typing import Dict, List, Any

class SemanticPatternAnalyzer:
    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        self.timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

        self.pii_keywords = [
            'name', 'firstname', 'lastname', 'surname', 'email', 'phone',
            'address', 'personal', 'private', 'confidential', 'secret',
            'inn', 'инн', 'snils', 'снилс', 'ogrn', 'огрн', 'огрнип',
            'card', 'карта', 'account', 'счет', 'personal', 'персональ'
        ]

    def analyze_semantic_patterns(self, key_stats: Dict) -> Dict[str, List[str]]:
        """Detect semantic patterns in data"""
        patterns = {
            'email_addresses': [],
            'phone_numbers': [],
            'dates': [],
            'timestamps': [],
            'identifiers': [],
            'financial_data': [],
            'personal_names': [],
            'addresses': [],
            'contact_info': []
        }

        for key, stats in key_stats.items():
            key_lower = key.lower()
            sample_values = stats.get('sample_values', [])

            # Email detection
            if 'email' in key_lower or any(self._is_email(val) for val in sample_values[:3]):
                patterns['email_addresses'].append(key)
                patterns['contact_info'].append(key)

            # Phone detection
            elif 'phone' in key_lower or 'телефон' in key_lower:
                patterns['phone_numbers'].append(key)
                patterns['contact_info'].append(key)

            # Date detection
            elif any(word in key_lower for word in ['date', 'дата', 'time', 'время']) or \
                 any(self._is_date(val) for val in sample_values[:3]):
                if any(self._is_timestamp(val) for val in sample_values[:3]):
                    patterns['timestamps'].append(key)
                else:
                    patterns['dates'].append(key)

            # Identifier detection (INN, OGRN, etc.) - include Russian financial IDs in financial_data
            elif any(word in key_lower for word in ['inn', 'инн', 'ogrn', 'огрн', 'snils', 'снилс']) or \
                 any(self._is_identifier(val) for val in sample_values[:3]):
                patterns['identifiers'].append(key)
                # Russian financial identifiers also go to financial_data
                if any(field in key_lower for field in ['innfl', 'ogrnip', 'insured_pf']):
                    patterns['financial_data'].append(key)

            # Personal names - universal detection
            elif self._is_personal_name_field(key_lower):
                patterns['personal_names'].append(key)

            # Financial data - universal pattern detection
            elif self._is_financial_field(key_lower, sample_values):
                patterns['financial_data'].append(key)

            # Address detection - universal pattern
            elif self._is_address_field(key_lower, sample_values):
                patterns['addresses'].append(key)

        return {k: v for k, v in patterns.items() if v}  # Remove empty lists

    def _is_financial_field(self, key_lower: str, sample_values: List) -> bool:
        """Enhanced financial field detection for Russian data"""
        # Critical Russian financial identifiers - highest priority
        if any(field in key_lower for field in ['innfl', 'ogrnip', 'insured_pf']):
            return True

        # Tax and legal identifiers
        if any(pattern in key_lower for pattern in ['inn', 'ogrn', 'snils', 'tax', 'pension']):
            return True

        # Banking related
        if any(pattern in key_lower for pattern in ['card', 'account', 'bank', 'payment']):
            return True

        # Insurance and financial services
        if any(pattern in key_lower for pattern in ['insured', 'insurance', 'financial', 'money']):
            return True

        # Check value patterns for numeric financial identifiers
        for val in sample_values[:3]:
            if val and isinstance(val, str):
                # Russian tax numbers patterns
                if len(val) in [10, 12] and val.isdigit():  # INN patterns
                    return True
                if len(val) == 13 and val.isdigit():  # OGRN patterns
                    return True
                if len(val) == 11 and val.isdigit():  # SNILS pattern
                    return True

        return False

    def _is_personal_name_field(self, key_lower: str) -> bool:
        """Universal personal name field detection"""
        name_indicators = [
            'name', 'firstname', 'lastname', 'surname', 'midname',
            'имя', 'фамилия', 'отчество', 'полное_имя'
        ]

        # Direct name field indicators
        for indicator in name_indicators:
            if indicator in key_lower:
                return True

        # Exclude company/organization names
        exclude_patterns = ['company', 'organization', 'firm', 'corp', 'filename', 'dirname']
        if any(pattern in key_lower for pattern in exclude_patterns):
            return False

        return False

    def _is_address_field(self, key_lower: str, sample_values: List) -> bool:
        """Universal address field detection"""
        address_indicators = [
            'address', 'street', 'city', 'region', 'location',
            'адрес', 'улица', 'город', 'регион', 'местоположение'
        ]

        for indicator in address_indicators:
            if indicator in key_lower:
                return True

        # Check for address-like content in values
        for val in sample_values[:3]:
            if val and isinstance(val, str) and len(val) > 20:
                # Common address keywords in content
                if any(word in val.lower() for word in ['street', 'avenue', 'boulevard', 'улица', 'проспект']):
                    return True

        return False

    def assess_pii_risk(self, key_stats: Dict, detected_patterns: Dict[str, List[str]]) -> float:
        """Assess PII risk with proper handling of hashed/anonymized data"""
        risk_score = 0.0
        total_fields = len(key_stats)

        if total_fields == 0:
            return 0.0

        # Check if data appears to be hashed/anonymized
        hashed_indicators = self._detect_hashed_data(key_stats)
        is_mostly_hashed = hashed_indicators['hash_ratio'] > 0.7

        # Adjusted weights for different types of PII
        if is_mostly_hashed:
            # Much lower weights for hashed data
            risk_weights = {
                'email_addresses': 0.05,    # Hashed emails are low risk
                'phone_numbers': 0.05,
                'personal_names': 0.0,      # Hashed names are not PII
                'identifiers': 0.1,         # Hashed IDs are low risk
                'financial_data': 0.15,     # Even financial hashes are low risk
                'addresses': 0.05,
                'dates': 0.02,
                'timestamps': 0.01,
                'contact_info': 0.05
            }
        else:
            # Standard weights for clear text data
            risk_weights = {
                'email_addresses': 0.4,
                'phone_numbers': 0.3,
                'personal_names': 0.5,
                'identifiers': 0.6,
                'financial_data': 0.7,
                'addresses': 0.3,
                'dates': 0.2,
                'timestamps': 0.1,
                'contact_info': 0.4
            }

        # Calculate base risk
        for pattern_type, fields in detected_patterns.items():
            if fields and pattern_type in risk_weights:
                field_ratio = len(fields) / total_fields
                risk_score += risk_weights[pattern_type] * field_ratio

        # Only apply combinations if data is not hashed
        if not is_mostly_hashed:
            has_identifiers = len(detected_patterns.get('identifiers', []) + detected_patterns.get('financial_data', [])) > 0
            has_names = len(detected_patterns.get('personal_names', [])) > 0
            has_contacts = len(detected_patterns.get('contact_info', []) + detected_patterns.get('email_addresses', [])) > 0
            has_birth_date = any('birth' in key.lower() or 'рождение' in key.lower() for key in key_stats.keys())

            # Critical combinations increase risk
            if has_identifiers and has_names:
                risk_score *= 1.5
            if has_identifiers and has_birth_date:
                risk_score *= 1.4
            if has_names and has_contacts:
                risk_score *= 1.3

            # Bonus for critical Russian identifiers
            critical_russian_ids = 0
            for key in key_stats.keys():
                key_lower = key.lower()
                if any(word in key_lower for word in ['innfl', 'ogrnip', 'snils']):
                    critical_russian_ids += 1

            if critical_russian_ids > 0:
                risk_score += 0.3 + (critical_russian_ids * 0.1)

            # Minimum high risk for critical data
            if has_identifiers or critical_russian_ids > 0:
                risk_score = max(risk_score, 0.75)
        else:
            # For hashed data, cap at low risk
            risk_score = min(risk_score, 0.2)

        return min(1.0, max(0.05, risk_score))

    def _detect_hashed_data(self, key_stats: Dict) -> Dict[str, Any]:
        """Detect if data appears to be hashed or anonymized"""
        hash_indicators = {
            'hash_count': 0,
            'total_fields': len(key_stats),
            'hash_ratio': 0.0,
            'hash_patterns': []
        }

        for key, stats in key_stats.items():
            key_lower = key.lower()
            sample_values = stats.get('sample_values', [])

            # Check for hash-like field names
            if any(indicator in key_lower for indicator in ['hash', 'hashed', 'anonymized', 'encrypted', 'masked']):
                hash_indicators['hash_count'] += 1
                hash_indicators['hash_patterns'].append(f"field_name: {key}")
                continue

            # Check for hash-like values (alphanumeric, consistent length)
            hash_like_values = 0
            for val in sample_values[:3]:
                if val and isinstance(val, str):
                    # Common hash patterns: long alphanumeric strings
                    if (len(val) >= 8 and
                        val.replace('_', '').isalnum() and
                        any(c.isdigit() for c in val) and
                        any(c.isalpha() for c in val)):
                        hash_like_values += 1

            # If most sample values look like hashes
            if hash_like_values >= len([v for v in sample_values[:3] if v]) * 0.7:
                hash_indicators['hash_count'] += 1
                hash_indicators['hash_patterns'].append(f"values: {key}")

        # Calculate hash ratio
        if hash_indicators['total_fields'] > 0:
            hash_indicators['hash_ratio'] = hash_indicators['hash_count'] / hash_indicators['total_fields']

        return hash_indicators

    def detect_domain_indicators(self, key_stats: Dict) -> List[str]:
        """Detect business domain indicators"""
        domains = []

        # Web analytics domain
        web_indicators = ['session', 'page', 'url', 'browser', 'device', 'referrer']
        if any(any(indicator in key.lower() for indicator in web_indicators) for key in key_stats.keys()):
            domains.append('web_analytics')

        # E-commerce domain
        ecommerce_indicators = ['purchase', 'cart', 'product', 'price', 'order']
        if any(any(indicator in key.lower() for indicator in ecommerce_indicators) for key in key_stats.keys()):
            domains.append('ecommerce')

        # Financial domain
        finance_indicators = ['payment', 'transaction', 'amount', 'balance', 'account']
        if any(any(indicator in key.lower() for indicator in finance_indicators) for key in key_stats.keys()):
            domains.append('financial')

        return domains

    def _is_email(self, value: str) -> bool:
        """Check if value is email"""
        if not isinstance(value, str):
            return False
        return bool(self.email_pattern.match(value))

    def _is_date(self, value: str) -> bool:
        """Check if value is date"""
        if not isinstance(value, str):
            return False
        return bool(self.date_pattern.search(value))

    def _is_timestamp(self, value: str) -> bool:
        """Check if value is timestamp"""
        if not isinstance(value, str):
            return False
        return bool(self.timestamp_pattern.search(value))

    def _is_identifier(self, value: str) -> bool:
        """Check if value looks like identifier"""
        if not isinstance(value, str):
            return False
        # Long alphanumeric strings, UUIDs
        if len(value) > 8 and (value.isalnum() or '-' in value):
            return True
        return False