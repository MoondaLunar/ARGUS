"""Analysis and matching utilities for cross-source correlation"""

import json
import logging
from typing import Dict, List, Tuple, Optional
from fuzzywuzzy import fuzz, process
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(message)s")


class FuzzyMatcher:
    """Cross-source entity matching with fuzzy comparison"""

    @staticmethod
    def find_similar_entities(entity: str, candidates: List[str], threshold: int = 75) -> List[Tuple[str, int]]:
        """Find similar entity names using fuzzy matching"""
        matches = process.extract(entity, candidates, scorer=fuzz.token_sort_ratio, limit=5)
        return [(match, score) for match, score in matches if score >= threshold]

    @staticmethod
    def match_across_sources(entities_source1: List[str], entities_source2: List[str], threshold: int = 70) -> List[Tuple[str, str, int]]:
        """Match entities across two different data sources"""
        matches = []
        for ent1 in entities_source1:
            similar = FuzzyMatcher.find_similar_entities(ent1, entities_source2, threshold)
            for ent2, score in similar:
                matches.append((ent1, ent2, score))
        return matches


class LocationIntelligence:
    """Geospatial analysis and clustering"""

    EARTH_RADIUS_KM = 6371

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in km"""
        import math
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return LocationIntelligence.EARTH_RADIUS_KM * c

    @staticmethod
    def cluster_locations(locations: List[Dict], radius_km: float = 1.0) -> List[List[Dict]]:
        """Cluster nearby locations together"""
        clusters = []
        remaining = list(locations)

        while remaining:
            seed = remaining.pop(0)
            cluster = [seed]

            i = 0
            while i < len(remaining):
                current = remaining[i]
                dist = LocationIntelligence.haversine_distance(
                    seed['latitude'], seed['longitude'],
                    current['latitude'], current['longitude']
                )
                if dist <= radius_km:
                    cluster.append(remaining.pop(i))
                else:
                    i += 1

            clusters.append(cluster)

        return clusters

    @staticmethod
    def timeline_from_locations(locations: List[Dict]) -> Dict:
        """Create a timeline of entity movements/sightings"""
        if not locations:
            return {}

        sorted_locs = sorted(locations, key=lambda x: x.get('timestamp', ''), reverse=False)
        timeline = defaultdict(list)

        for loc in sorted_locs:
            timestamp = loc.get('timestamp', 'unknown')
            timeline[timestamp].append({
                'lat': loc.get('latitude'),
                'lon': loc.get('longitude'),
                'source': loc.get('source'),
                'confidence': loc.get('confidence', 0.0)
            })

        return dict(timeline)


class CorrelationAnalyzer:
    """Advanced multi-source correlation analysis"""

    @staticmethod
    def find_co_occurrences(documents: List[Dict], entities: List[str], min_docs: int = 2) -> List[Dict]:
        """Find entities that appear together in multiple documents"""
        co_occurrences = defaultdict(list)

        for doc in documents:
            doc_entities = set()
            text = doc.get('text', '').lower()
            for entity in entities:
                if entity.lower() in text:
                    doc_entities.add(entity)

            for i, ent1 in enumerate(doc_entities):
                for ent2 in list(doc_entities)[i+1:]:
                    key = tuple(sorted([ent1, ent2]))
                    co_occurrences[key].append(doc.get('id', 'unknown'))

        result = []
        for (ent1, ent2), doc_ids in co_occurrences.items():
            if len(doc_ids) >= min_docs:
                result.append({
                    'entity_a': ent1,
                    'entity_b': ent2,
                    'co_occurrence_count': len(doc_ids),
                    'documents': doc_ids,
                    'strength': min(1.0, len(doc_ids) / 10.0)
                })

        return sorted(result, key=lambda x: x['strength'], reverse=True)

    @staticmethod
    def detect_metadata_patterns(documents: List[Dict]) -> Dict:
        """Find patterns in metadata across documents"""
        patterns = {
            'common_cameras': defaultdict(int),
            'common_locations': defaultdict(int),
            'common_timestamps': defaultdict(int),
            'document_clustering': defaultdict(list)
        }

        for doc in documents:
            metadata = doc.get('metadata', {})

            # Camera clustering
            camera = f"{metadata.get('camera_make', 'unknown')} {metadata.get('camera_model', 'unknown')}".strip()
            if camera != 'unknown unknown':
                patterns['common_cameras'][camera] += 1

            # Location clustering
            if 'gps' in metadata:
                patterns['common_locations'][metadata['gps']] += 1

            # Timestamp patterns
            timestamp = metadata.get('date_taken', 'unknown')
            patterns['common_timestamps'][timestamp] += 1

        return {k: dict(v) for k, v in patterns.items()}

    @staticmethod
    def entity_behavior_timeline(entity: str, events: List[Dict]) -> Dict:
        """Build a behavioral timeline for an entity"""
        timeline = defaultdict(list)

        for event in events:
            if entity in event.get('entities', []):
                timestamp = event.get('timestamp', '')
                timeline[timestamp].append({
                    'event_type': event.get('type'),
                    'location': event.get('location'),
                    'source': event.get('source'),
                    'confidence': event.get('confidence', 0.5)
                })

        return dict(sorted(timeline.items()))

    @staticmethod
    def calculate_relationship_strength(link_count: int, avg_confidence: float, link_types: List[str]) -> float:
        """Calculate overall strength of a relationship"""
        type_bonus = len(set(link_types)) * 0.1  # Bonus for diverse evidence types
        frequency_bonus = min(0.3, link_count * 0.05)
        confidence_component = avg_confidence * 0.6

        return min(1.0, confidence_component + frequency_bonus + type_bonus)


class ExportFormatter:
    """Format analysis results for export"""

    @staticmethod
    def export_knowledge_graph(links: List[Dict], entities: List[str]) -> Dict:
        """Export as knowledge graph JSON"""
        nodes = [{'id': ent, 'type': 'entity'} for ent in entities]
        edges = []

        for link in links:
            edges.append({
                'source': link['entityA'],
                'target': link['entityB'],
                'weight': link['confidence'],
                'type': link.get('link_type', 'entity_co-occurrence'),
                'evidence': link.get('rationale')
            })

        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'entity_count': len(entities),
                'link_count': len(edges),
                'avg_confidence': sum(e['weight'] for e in edges) / len(edges) if edges else 0
            }
        }

    @staticmethod
    def export_timeline(events: List[Dict]) -> Dict:
        """Export timeline view"""
        return {
            'events': sorted(events, key=lambda x: x.get('timestamp', '')),
            'date_range': {
                'earliest': min((e.get('timestamp', '') for e in events), default=''),
                'latest': max((e.get('timestamp', '') for e in events), default='')
            }
        }

    @staticmethod
    def export_location_heat_map(clusters: List[Dict]) -> Dict:
        """Export location data for heat mapping"""
        return {
            'clusters': [
                {
                    'center': {
                        'lat': sum(loc['latitude'] for loc in cluster) / len(cluster),
                        'lon': sum(loc['longitude'] for loc in cluster) / len(cluster)
                    },
                    'radius': cluster[0].get('radius', 1.0),
                    'intensity': len(cluster),
                    'entities': [loc.get('entity', '') for loc in cluster]
                }
                for cluster in clusters
            ]
        }

    @staticmethod
    def export_entity_relationship_report(entity: str, connections: List[Dict]) -> Dict:
        """Export detailed report for a single entity"""
        high_confidence = [c for c in connections if c.get('confidence', 0) >= 0.7]
        medium_confidence = [c for c in connections if 0.5 <= c.get('confidence', 0) < 0.7]
        low_confidence = [c for c in connections if c.get('confidence', 0) < 0.5]

        return {
            'entity': entity,
            'total_connections': len(connections),
            'high_confidence': {
                'count': len(high_confidence),
                'connections': high_confidence
            },
            'medium_confidence': {
                'count': len(medium_confidence),
                'connections': medium_confidence
            },
            'low_confidence': {
                'count': len(low_confidence),
                'connections': low_confidence
            },
            'summary': {
                'most_likely_association': high_confidence[0] if high_confidence else None,
                'evidence_diversity': len(set(c.get('link_type') for c in connections))
            }
        }
