import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { LatLngExpression } from "leaflet";

import Menu from "./Menu";

// const apiEndpoint = "http://localhost:8000/api";
// const apiEndpoint = "http://192.168.0.15:8000/api";
// const apiEndpoint = "http://localhost:58888/api";
const apiEndpoint = "https://smagomap-api.mryutaro.site/api";
const zoomLevel = 20;

interface MapComponentProps {
    position: LatLngExpression;
}

const MapComponent: React.FC<MapComponentProps> = ({ position }) => {
    const map = useMap();

    useEffect(() => {
        if (position) {
            map.setView(position, zoomLevel);
        }
    }, [map, position]);

    return null;
};

const Map: React.FC = () => {
    const [position, setPosition] = useState<LatLngExpression | null>(null);
    const [trashcans, setTrashcans] = useState<Array<{ id: number; latitude: number; longitude: number; status: string }>>([]);
    const [requests, setRequests] = useState<Array<{ id: number; latitude: number; longitude: number }>>([]);

    useEffect(() => {
        // FastAPIのエンドポイントからゴミ箱の位置を取得
        fetch(apiEndpoint + "/trashcans")
            .then((response) => response.json())
            .then((data) => setTrashcans(data.trashcans))
            .catch((error) => console.error("Error fetching trashcans:", error));
    }, []);

    useEffect(() => {
        // FastAPIのエンドポイントからリクエストの位置を取得
        fetch(apiEndpoint + "/requests")
            .then((response) => response.json())
            .then((data) => setRequests(data.requests))
            .catch((error) => console.error("Error fetching requests:", error));
    }, []);

    useEffect(() => {
        // ユーザーの位置を取得
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const { latitude, longitude } = pos.coords;
                setPosition([latitude, longitude]);
            },
            (err) => {
                console.error(err);
            }
        );
    }, []);

    const getMarkerIcon = (status: string) => {
        let iconUrl;
        if (status === "full") {
            iconUrl = "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png";
        } else if (status === "not_full") {
            iconUrl = "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png";
        } else if (status === "removed") {
            iconUrl = "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-grey.png";
        } else {
            iconUrl = "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png";
        }
        return L.icon({
            iconUrl,
            shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
        });
    };

    return (
        <>
            <MapContainer
                center={position || [35.7137757, 139.7969451]}
                zoom={zoomLevel}
                style={{ height: "100vh", width: "100vw" }}
                zoomControl={false} // ズームコントロールを非表示に設定
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {position && (
                    <>
                        <CircleMarker center={position} pathOptions={{ color: "white" }} radius={10} />
                        <CircleMarker center={position} pathOptions={{ fillColor: "blue", fillOpacity: 1 }} radius={10} />
                    </>
                )}
                {/* ゴミ箱の位置にマーカーを配置 */}
                {trashcans
                    .filter((trashcan) => trashcan.status !== "removed") // Optionally filter out removed
                    .map((trashcan) => (
                        <Marker key={trashcan.id} position={[trashcan.latitude, trashcan.longitude]} icon={getMarkerIcon(trashcan.status)}>
                            <Popup>
                                id: {trashcan.id} <br /> status: {trashcan.status}
                            </Popup>
                        </Marker>
                    ))}
                {/* リクエストの位置に点を配置 */}
                {requests.map((request) => (
                    <Circle key={request.id} center={[request.latitude, request.longitude]} radius={1} color="red">
                        <Popup>request {request.id}</Popup>
                    </Circle>
                ))}

                {position && <MapComponent position={position} />}
            </MapContainer>

            <Menu />
        </>
    );
};

export default Map;
