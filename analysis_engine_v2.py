"""Optimized analysis and matching utilities with caching and performance improvements"""

import json
import logging
import math
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
from fuzzywuzzy import fuzz, process
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class FuzzyMatcher:
    """Cross-source entity matching with fuzzy comparison and caching"""

    @staticmethod
    @lru_cache(maxsize=512)
    def _cached_similarity(entity: str, candidate: str, scorer_type: str = "token_sort") -> int:
        """Cached fuzzy similarity calculation"""
        if scorer_type == "token_sort":
            return fuzz.token_sort_ratio(entity, candidate)
        elif scorer_type == "ratio":
            return fuzz.ratio(entity, candidate)
        return fuzz.partial_ratio(entity, candidate)

    @staticmethod
    def find_similar_entities(entity: str, candidates: List[str], threshold: int = 75) -> List[Tuple[str, int]]:
        """Find similar entity names using fuzzy matching with caching"""
        matches = process.extract(entity, candidates, scorer=fuzz.token_sort_ratio, limit=5)
        return [(match, score) for match, score in matches if score >= threshold]

    @staticmethod
    def match_across_sources(entities_source1: List[str], entities_source2: List[str], 
                            threshold: int = 70, use_cache: bool = True) -> List[Tuple[str, str, int]]:
        """Match entities across two different data sources"""
        matches = []
        candidates_set = set(entities_source2)

        for ent1 in entities_source1:
            similar = FuzzyMatcher.find_similar_entities(ent1, list(candidates_set), threshold)
            for ent2, score in similar:
                matches.append((ent1, ent2, score))

        return matches


class LocationIntelligence:
    """Geospatial analysis and clustering with optimizations"""

    EARTH_RADIUS_KM = 6371

    @staticmethod
    @lru_cache(maxsize=4096)
    def haversine_distance(lat1_key: str, lon1_key: str, lat2_key: str, lon2_key: str) -> float:
        """Calculate distance between two GPS coordinates (cached version)
        
        Args: String representations of coordinates for caching
        """
        lat1, lon1, lat2, lon2 = float(lat1_key), float(lon1_key), float(lat2_key), float(lon2_key)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return LocationIntelligence.EARTH_RADIUS_KM * c

    @staticmethod
    def cluster_locations(locations: List[Dict], radius_km: float = 1.0) -> List[List[Dict]]:
        """Cluster nearby locations using optimized algorithm"""
        if not locations:
            return []

        clusters = []
        remaining = list(locations)

        while remaining:
            seed = remaining.pop(0)
            cluster = [seed]

            i = 0
            seed_lat_key = str(seed['latitude'])
            seed_lon_key = str(seed['longitude'])

            while i < len(remaining):
                current = remaining[i]
                dist = LocationIntelligence.haversine_distance(
                    seed_lat_key, seed_lon_key,
                    str(current['latitude']), str(current['longitude'])
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

    @staticmethod
    def cluster_by_geohash(gps_points: List[Dict], precision: int = 5) -> Dict[str, List[Dict]]:
        """Cluster GPS points by geohash for fast proximity queries"""
        clusters = defaultdict(list)

        for point in gps_points:
            lat = round(point.get('latitude', 0), precision)
            lon = round(point.get('longitude', 0), precision)
            geohash = f"{lat},{lon}"
            clusters[geohash].append(point)

        return dict(clusters)


class CorrelationAnalyzer:
    """Advanced multi-source correlation analysis with optimizations"""

    @staticmethod
    def find_co_occurrences(documents: List[Dict], entities: List[str], min_docs: int = 2) -> List[Dict]:
        """Find entities that appear together in multiple documents"""
        co_occurrences = defaultdict(list)
        entity_lower = {ent: ent.lower() for ent in entities}

        for doc in documents:
            doc_entities = set()
            text = doc.get('text', '').lower()

            for entity in entities:
                if entity_lower[entity] in text:
                    doc_entities.add(entity)

            for i, ent1 in enumerate(list(doc_entities)):
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
            'camera_location_pairs': defaultdict(int),
        }

        for doc in documents:
            metadata = doc.get('metadata', {})

            # Camera clustering
            camera_make = metadata.get('camera_make', '').strip()
            camera_model = metadata.get('camera_model', '').strip()

            if camera_make and camera_model:
                camera = f"{camera_make} {camera_model}"
                patterns['common_cameras'][camera] += 1

                # Camera + Location pairs (useful for attribution)
                if 'gps' in metadata:
                    pair = f"{camera}@{metadata['gps']}"
                    patterns['camera_location_pairs'][pair] += 1

            # Location clustering
            if 'gps' in metadata:
                patterns['common_locations'][metadata['gps']] += 1

            # Timestamp patterns
            timestamp = metadata.get('date_taken', 'unknown')
            if timestamp != 'unknown':
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
        """Calculate overall strength of a relationship with weights"""
        type_bonus = len(set(link_types)) * 0.1  # Bonus for diverse evidence types
        frequency_bonus = min(0.3, link_count * 0.05)
        confidence_component = avg_confidence * 0.6

        return min(1.0, confidence_component + frequency_bonus + type_bonus)

    @staticmethod
    def find_entity_clusters(entities: List[str], connections: List[Dict], 
                            min_connection_strength: float = 0.5) -> List[List[str]]:
        """Find groups of related entities (simple community detection)"""
        graph = defaultdict(set)

        for conn in connections:
            if conn.get('confidence', 0) >= min_connection_strength:
                ent_a = conn.get('entityA')
                ent_b = conn.get('entityB')
                if ent_a and ent_b:
                    graph[ent_a].add(ent_b)
                    graph[ent_b].add(ent_a)

        visited = set()
        clusters = []

        for entity in entities:
            if entity in visited:
                continue

            cluster = set()
            stack = [entity]

            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                cluster.add(current)

                for neighbor in graph.get(current, []):
                    if neighbor not in visited:
                        stack.append(neighbor)

            if cluster:
                clusters.append(list(cluster))

        return clusters


class ExportFormatter:
    """Format analysis results for export with optimizations"""

    @staticmethod
    def export_knowledge_graph(links: List[Dict], entities: List[str]) -> Dict:
        """Export as knowledge graph JSON"""
        nodes = [{'id': ent, 'type': 'entity', 'label': ent} for ent in entities]
        edges = []
        edge_set = set()  # Deduplicate edges

        for link in links:
            edge_key = tuple(sorted([link['entityA'], link['entityB']]))
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append({
                    'source': link['entityA'],
                    'target': link['entityB'],
                    'weight': link['confidence'],
                    'type': link.get('link_type', 'entity_co-occurrence'),
                    'evidence': link.get('rationale'),
                    'metadata': link.get('metadata_evidence')
                })

        avg_confidence = sum(e['weight'] for e in edges) / len(edges) if edges else 0

        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'entity_count': len(entities),
                'link_count': len(edges),
                'avg_confidence': round(avg_confidence, 3),
                'graph_density': round(len(edges) / (len(entities) * (len(entities) - 1) / 2) if len(entities) > 1 else 0, 3)
            }
        }

    @staticmethod
    def export_timeline(events: List[Dict]) -> Dict:
        """Export timeline view"""
        sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))

        return {
            'events': sorted_events,
            'date_range': {
                'earliest': sorted_events[0].get('timestamp', '') if sorted_events else '',
                'latest': sorted_events[-1].get('timestamp', '') if sorted_events else ''
            },
            'event_count': len(sorted_events)
        }

    @staticmethod
    def export_location_heat_map(clusters: List[List[Dict]]) -> Dict:
        """Export location data for heat mapping"""
        heat_clusters = []

        for cluster in clusters:
            if not cluster:
                continue

            lats = [loc['latitude'] for loc in cluster]
            lons = [loc['longitude'] for loc in cluster]

            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)

            # Calculate cluster radius
            max_dist = 0
            for loc in cluster:
                dist = math.sqrt((loc['latitude'] - center_lat) ** 2 + (loc['longitude'] - center_lon) ** 2)
                max_dist = max(max_dist, dist)

            heat_clusters.append({
                'center': {'lat': round(center_lat, 6), 'lon': round(center_lon, 6)},
                'radius': round(max_dist, 6),
                'intensity': len(cluster),
                'entities': list(set(loc.get('entity', '') for loc in cluster if loc.get('entity')))
            })

        return {
            'clusters': heat_clusters,
            'cluster_count': len(heat_clusters),
            'total_points': sum(c['intensity'] for c in heat_clusters)
        }

    @staticmethod
    def export_entity_relationship_report(entity: str, connections: List[Dict]) -> Dict:
        """Export detailed report for a single entity"""
        high_confidence = [c for c in connections if c.get('confidence', 0) >= 0.7]
        medium_confidence = [c for c in connections if 0.5 <= c.get('confidence', 0) < 0.7]
        low_confidence = [c for c in connections if c.get('confidence', 0) < 0.5]

        # Calculate link type distribution
        link_types = defaultdict(int)
        for conn in connections:
            link_types[conn.get('link_type', 'unknown')] += 1

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
                'evidence_diversity': len(dict(link_types)),
                'evidence_types': dict(link_types),
                'avg_confidence': round(sum(c.get('confidence', 0) for c in connections) / len(connections), 3) if connections else 0
            }
        }

    @staticmethod
    def export_threat_assessment(entity: str, connections: List[Dict], 
                                events: List[Dict] = None) -> Dict:
        """Generate threat assessment for entity based on connections and activity"""
        assessment = {
            'entity': entity,
            'risk_level': 'low'
        }

        # Calculate risk based on connection count and confidence
        high_confidence_count = sum(1 for c in connections if c.get('confidence', 0) >= 0.75)
        avg_confidence = sum(c.get('confidence', 0) for c in connections) / len(connections) if connections else 0

        risk_score = (high_confidence_count * 0.3 + avg_confidence * 70) / 100

        if risk_score >= 0.75:
            assessment['risk_level'] = 'critical'
        elif risk_score >= 0.5:
            assessment['risk_level'] = 'high'
        elif risk_score >= 0.3:
            assessment['risk_level'] = 'medium'

        assessment['risk_score'] = round(risk_score, 3)
        assessment['high_confidence_connections'] = high_confidence_count
        assessment['avg_connection_strength'] = round(avg_confidence, 3)

        if events:
            assessment['recent_activity'] = len([e for e in events if e.get('entities') and entity in e['entities']])

        return assessment
