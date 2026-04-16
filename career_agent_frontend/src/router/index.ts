import { createRouter, createWebHistory } from 'vue-router'
import PlanningLayout from '../layout/PlanningLayout.vue'
import JobLayout from '../layout/JobLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue')
    },
    {
      path: '/',
      name: 'modeSelect',
      component: () => import('../views/mode/ModeSelectView.vue')
    },
    {
      path: '/planning',
      component: PlanningLayout,
      children: [
        {
          path: '',
          name: 'planningHome',
          component: () => import('../views/planning/PlanningHomeView.vue')
        },
        {
          path: 'profile',
          name: 'planningProfile',
          component: () => import('../views/planning/PlanningProfileView.vue')
        },
        {
          path: 'explore',
          name: 'planningExplore',
          component: () => import('../views/planning/ExploreView.vue')
        },
        {
          path: 'path',
          name: 'planningPath',
          component: () => import('../views/planning/PathRecommendationView.vue')
        },
        {
          path: 'plan',
          name: 'planningPlan',
          component: () => import('../views/planning/GrowthPlanView.vue')
        },
        {
          path: 'resources',
          name: 'planningResources',
          component: () => import('../views/planning/ResourcesView.vue')
        }
      ]
    },
    {
      path: '/job',
      component: JobLayout,
      children: [
        {
          path: '',
          name: 'jobHome',
          component: () => import('../views/job/JobHomeView.vue')
        },
        {
          path: 'position-profiles',
          name: 'positionProfiles',
          component: () => import('../views/job/PositionProfilesView.vue')
        },
        {
          path: 'career-graph',
          name: 'careerGraph',
          component: () => import('../views/job/CareerGraphView.vue')
        },
        {
          path: 'profile',
          name: 'jobProfile',
          component: () => import('../views/job/JobProfileView.vue')
        },
        {
          path: 'resume',
          name: 'jobResume',
          component: () => import('../views/job/JobResumeView.vue')
        },
        {
          path: 'match',
          name: 'jobMatch',
          component: () => import('../views/job/JobMatchView.vue')
        },
        {
          path: 'report',
          name: 'jobReport',
          component: () => import('../views/job/JobReportView.vue')
        },
        {
          path: 'history',
          name: 'jobHistory',
          component: () => import('../views/job/JobHistoryView.vue')
        }
      ]
    }
  ]
})

export default router