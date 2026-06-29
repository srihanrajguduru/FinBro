"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const { data: notifications, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.getNotifications(),
  });

  const markAllMutation = useMutation({
    mutationFn: () => api.markAllNotificationsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      toast.success("All marked as read");
    },
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => api.markNotificationRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const unread = (notifications || []).filter((n) => !n.read);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-muted-foreground">{unread.length} unread</p>
        </div>
        {unread.length > 0 && (
          <Button variant="outline" onClick={() => markAllMutation.mutate()}>Mark all read</Button>
        )}
      </div>

      <div className="space-y-3">
        {(notifications || []).map((n) => (
          <Card key={n.id} className={n.read ? "opacity-60" : "border-primary/30"}>
            <CardContent className="flex items-start justify-between pt-6">
              <div>
                <p className="font-medium">{n.title}</p>
                <p className="mt-1 text-sm text-muted-foreground">{n.message}</p>
                <p className="mt-2 text-xs text-muted-foreground">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              {!n.read && (
                <Button size="sm" variant="ghost" onClick={() => markReadMutation.mutate(n.id)}>Read</Button>
              )}
            </CardContent>
          </Card>
        ))}
        {!isLoading && !notifications?.length && (
          <p className="py-12 text-center text-muted-foreground">No notifications</p>
        )}
      </div>
    </div>
  );
}
