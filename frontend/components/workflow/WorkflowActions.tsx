'use client';

import React, { useState } from 'react';
import type { ChangeEvent } from 'react';
import { Button, Modal, Textarea, Badge } from '@/components/ui';
import type { WorkflowAvailableAction } from '@/types/workflow';

interface WorkflowActionsProps {
  currentState?: string;
  availableActions: WorkflowAvailableAction[];
  isTransitioning?: boolean;
  onTransition: (input: { action: string; comment?: string }) => Promise<unknown>;
}

const ACTION_LABELS: Record<string, string> = {
  submit: 'Submit',
  approve: 'Approve',
  reject: 'Reject',
  certify: 'Certify',
  issue: 'Issue',
  deliver: 'Mark Delivered',
  invoice: 'Mark Invoiced',
  pay: 'Mark Paid',
  activate: 'Activate',
  complete: 'Complete',
  terminate: 'Terminate',
};

export function WorkflowActions({ currentState, availableActions, isTransitioning = false, onTransition }: WorkflowActionsProps) {
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [comment, setComment] = useState('');

  const requiresComment = selectedAction === 'reject' || selectedAction === 'terminate';

  const closeModal = () => {
    setSelectedAction(null);
    setComment('');
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-600">Current State</span>
        <Badge variant="secondary">{currentState || 'Unknown'}</Badge>
      </div>

      <div className="flex flex-wrap gap-2">
        {availableActions.length === 0 ? (
          <span className="text-sm text-gray-500">No actions available for your role.</span>
        ) : (
          availableActions.map((item) => (
            <Button
              key={`${item.action}-${item.to_state}`}
              size="sm"
              variant={item.action === 'reject' || item.action === 'terminate' ? 'destructive' : 'primary'}
              disabled={isTransitioning}
              onClick={() => setSelectedAction(item.action)}
            >
              {ACTION_LABELS[item.action] || item.action}
            </Button>
          ))
        )}
      </div>

      <Modal
        isOpen={Boolean(selectedAction)}
        onClose={closeModal}
        title={selectedAction ? `${ACTION_LABELS[selectedAction] || selectedAction} Confirmation` : 'Confirm'}
        size="md"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={closeModal} disabled={isTransitioning}>
              Cancel
            </Button>
            <Button
              variant={selectedAction === 'reject' || selectedAction === 'terminate' ? 'destructive' : 'primary'}
              isLoading={isTransitioning}
              disabled={requiresComment && !comment.trim()}
              onClick={async () => {
                if (!selectedAction) return;
                await onTransition({ action: selectedAction, comment: comment.trim() || undefined });
                closeModal();
              }}
            >
              Confirm
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-sm text-gray-700">Add an optional comment for this transition.</p>
          <Textarea
            label="Comment"
            value={comment}
            onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setComment(event.target.value)}
            placeholder="Enter comment"
            required={requiresComment}
            rows={4}
          />
        </div>
      </Modal>
    </div>
  );
}
