import type { ChapterDef } from "./types";
import HookChapter from "../chapters/01-hook/Hook";
import { narrations as hookNarrations } from "../chapters/01-hook/narrations";
import DataChapter from "../chapters/02-data/Data";
import { narrations as dataNarrations } from "../chapters/02-data/narrations";
import DayClock from "../chapters/03-day-clock/DayClock";
import { narrations as dayNarrations } from "../chapters/03-day-clock/narrations";
import NightClock from "../chapters/04-night-clock/NightClock";
import { narrations as nightNarrations } from "../chapters/04-night-clock/narrations";
import Space from "../chapters/05-space/Space";
import { narrations as spaceNarrations } from "../chapters/05-space/narrations";
import DeepData from "../chapters/06-deep-data/DeepData";
import { narrations as deepDataNarrations } from "../chapters/06-deep-data/narrations";
import Invasion from "../chapters/07-invasion/Invasion";
import { narrations as invasionNarrations } from "../chapters/07-invasion/narrations";
import Action from "../chapters/08-action/Action";
import { narrations as actionNarrations } from "../chapters/08-action/narrations";

export const CHAPTERS: ChapterDef[] = [
  {
    id: "hook",
    title: "開場",
    narrations: hookNarrations,
    Component: HookChapter,
  },
  {
    id: "data",
    title: "數據基礎",
    narrations: dataNarrations,
    Component: DataChapter,
  },
  {
    id: "day-clock",
    title: "白天的時鐘",
    narrations: dayNarrations,
    Component: DayClock,
  },
  {
    id: "night-clock",
    title: "夜晚的時鐘",
    narrations: nightNarrations,
    Component: NightClock,
  },
  {
    id: "space",
    title: "空間維度",
    narrations: spaceNarrations,
    Component: Space,
  },
  {
    id: "deep-data",
    title: "深度數據",
    narrations: deepDataNarrations,
    Component: DeepData,
  },
  {
    id: "invasion",
    title: "外來入侵物種",
    narrations: invasionNarrations,
    Component: Invasion,
  },
  {
    id: "action",
    title: "行動建議",
    narrations: actionNarrations,
    Component: Action,
  },
];
