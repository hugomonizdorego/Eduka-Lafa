"""Session-only reminders; no system scheduler or background persistence."""
from dataclasses import dataclass
import time

@dataclass
class Reminder:
    id: int
    text: str
    due: float

class Reminders:
    def __init__(self,clock=time.monotonic):self.clock=clock;self.items=[];self.next_id=1
    def add(self,minutes,text):
        minutes=float(minutes);text=text.strip()
        if not 1<=minutes<=1440:raise ValueError('Reminder must be between 1 minute and 24 hours.')
        if not text or len(text)>240:raise ValueError('Enter a reminder of 1–240 characters.')
        reminder=Reminder(self.next_id,text,self.clock()+minutes*60);self.items.append(reminder);self.next_id+=1
        return reminder
    def cancel(self,identifier):self.items=[item for item in self.items if item.id!=identifier]
    def due(self,online):
        if not online:return []
        expired=[item for item in self.items if item.due<=self.clock()]
        self.items=[item for item in self.items if item not in expired]
        return expired
    def remaining(self,item):return max(0,int(item.due-self.clock()))
