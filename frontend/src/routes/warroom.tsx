import { createFileRoute } from "@tanstack/react-router";
import { WarRoom } from "@/components/WarRoom";
import { useNavigate } from "@tanstack/react-router";

export const Route = createFileRoute("/warroom")({
  component: WarRoomPage,
});

function WarRoomPage() {
  const navigate = useNavigate();

  const handleClose = () => {
    navigate({ to: "/" });
  };

  return <WarRoom onClose={handleClose} />;
}
