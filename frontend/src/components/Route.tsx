import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { LatLngExpression } from "leaflet";
import polyline from "@mapbox/polyline";

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
    const [route, setRoute] = useState<[number, number][]>([]);
    const [routeRadius, setRouteRadius] = useState<number>(0);

    useEffect(() => {
        // FastAPIのエンドポイントからゴミ箱の位置を取得
        fetch(apiEndpoint + "/trashcans")
            .then((response) => response.json())
            .then((data) => setTrashcans(data.trashcans))
            .catch((error) => console.error("Error fetching trashcans:", error));
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

    useEffect(() => {
        const fetchRoute = async () => {
            try {
                // 現在の位置を取得する
                navigator.geolocation.getCurrentPosition(async (position) => {
                    const { latitude, longitude } = position.coords;
                    console.log("Current Position:", latitude, longitude);

                    // 位置情報を含むリクエストを送信
                    const response = await fetch(apiEndpoint + "/route", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            origin: {
                                latitude: latitude,
                                longitude: longitude,
                                // latitude: 35.72285883534467,
                                // longitude: 139.80149745941165,
                            },
                            destination: {
                                latitude: latitude,
                                longitude: longitude,
                                // latitude: 35.72285883534467,
                                // longitude: 139.80149745941165,
                            },
                        }),
                    });

                    const data = await response.json();
                    const decodedRoute = polyline.decode(data.polyline_points);
                    console.log("Decoded Route:", decodedRoute);
                    setRouteRadius(data.radius);
                    setRoute(decodedRoute);
                });
            } catch (error) {
                console.error("Error fetching route:", error);
            }
        };
        fetchRoute();
    }, []);

    // useEffect(() => {
    //     const fetchRoute = async () => {
    //         try {
    //             // 位置情報を含むリクエストを送信
    //             const response = await fetch(apiEndpoint + "/route", {
    //                 method: "POST",
    //                 headers: {
    //                     "Content-Type": "application/json",
    //                 },
    //                 body: JSON.stringify({
    //                     origin: {
    //                         // latitude: latitude,
    //                         // longitude: longitude,
    //                         latitude: 35.72285883534467,
    //                         longitude: 139.80149745941165,
    //                     },
    //                     destination: {
    //                         // latitude: latitude,
    //                         // longitude: longitude,
    //                         latitude: 35.72285883534467,
    //                         longitude: 139.80149745941165,
    //                     },
    //                 }),
    //             });

    //             const data = await response.json();
    //             const decodedRoute = polyline.decode(data.polyline_points);
    //             console.log("Decoded Route:", decodedRoute);
    //             alert(data.radius);
    //             setRouteRadius(data.radius);
    //             setRoute(decodedRoute);
    //         } catch (error) {
    //             alert("error");
    //             console.error("Error fetching route:", error);
    //         }
    //     };
    //     fetchRoute();
    // }, []);

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

    if (!position) {
        return <div>Loading...</div>; // 位置情報が取得できるまで表示
    }

    return (
        <>
            <MapContainer
                center={position}
                zoom={zoomLevel}
                style={{ height: "100vh", width: "100vw" }}
                zoomControl={false} // ズームコントロールを非表示に設定
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <CircleMarker center={position} pathOptions={{ color: "white" }} radius={10} />
                <CircleMarker center={position} pathOptions={{ fillColor: "blue", fillOpacity: 1 }} radius={10} />
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

                {route.length > 0 && <Polyline positions={route} color="blue" />}
                {routeRadius > 0 && (
                    <>
                        {/* 半径 */}
                        <Circle
                            center={position}
                            // center={[35.72285883534467, 139.80149745941165]}
                            radius={routeRadius}
                        />
                        {/* 中心 */}
                        <CircleMarker
                            center={position}
                            // center={[35.72285883534467, 139.80149745941165]}
                            pathOptions={{ color: "white" }}
                            radius={10}
                        />
                        <CircleMarker
                            center={position}
                            // center={[35.72285883534467, 139.80149745941165]}
                            pathOptions={{ fillColor: "blue", fillOpacity: 1 }}
                            radius={10}
                        />
                    </>
                )}

                <MapComponent position={position} />
            </MapContainer>

            <Menu />
        </>
    );
};

export default Map;
